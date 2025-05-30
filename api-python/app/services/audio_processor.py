import os
import tempfile
import uuid
from typing import Dict, Optional
from datetime import datetime
import aiofiles
from fastapi import UploadFile, HTTPException

from app.services.whisper_service import whisper_service
from app.services.minio_service import minio_service
from app.config import settings

class AudioProcessor:
    """Audio processing service for legal recordings with Whisper transcription"""
    
    def __init__(self):
        self.allowed_formats = ['.m4a', '.mp3', '.wav', '.flac', '.aac', '.ogg']
        self.max_file_size = 500 * 1024 * 1024  # 500MB max
        
    async def process_recording_upload(
        self,
        file: UploadFile,
        metadata: Dict,
        user_id: str
    ) -> Dict:
        """
        Process uploaded legal recording:
        1. Validate audio file
        2. Store in MinIO
        3. Trigger Whisper transcription
        4. Store results
        """
        recording_id = str(uuid.uuid4())
        
        try:
            # Validate file
            self._validate_audio_file(file)
            
            # Read file content
            content = await file.read()
            
            # Store original recording in MinIO
            storage_path = await self._store_recording(
                user_id, recording_id, content, file.filename, metadata
            )
            
            # Create temporary file for transcription
            temp_path = await self._create_temp_file(content, file.filename)
            
            try:
                # Start transcription process
                transcription_result = await self._transcribe_recording(
                    temp_path, metadata, recording_id
                )
                
                # Store transcription in MinIO
                transcription_path = await self._store_transcription(
                    user_id, recording_id, transcription_result
                )
                
                # Create processing summary
                processing_result = {
                    "recording_id": recording_id,
                    "status": "completed",
                    "processed_at": datetime.utcnow().isoformat(),
                    "file_info": {
                        "name": file.filename,
                        "size": file.size,
                        "type": file.content_type,
                        "storage_path": storage_path
                    },
                    "transcription": {
                        "text": transcription_result["text"],
                        "formatted_transcript": transcription_result["formatted_transcript"],
                        "storage_path": transcription_path,
                        "duration_seconds": transcription_result["metadata"]["audio_duration"],
                        "word_count": transcription_result["word_count"],
                        "confidence_score": transcription_result["confidence_score"],
                        "legal_terms_detected": transcription_result["legal_terms_detected"],
                        "processing_time": transcription_result["processing_time_seconds"]
                    },
                    "metadata": metadata
                }
                
                # Store processing results
                results_path = await self._store_processing_results(
                    user_id, recording_id, processing_result
                )
                
                processing_result["results_storage_path"] = results_path
                
                return processing_result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            # Create error result
            error_result = {
                "recording_id": recording_id,
                "status": "failed",
                "processed_at": datetime.utcnow().isoformat(),
                "error": str(e),
                "metadata": metadata
            }
            
            # Try to store error result
            try:
                await self._store_processing_results(user_id, recording_id, error_result)
            except:
                pass  # Don't fail completely if we can't store the error
            
            return error_result
    
    def _validate_audio_file(self, file: UploadFile) -> None:
        """Validate uploaded audio file"""
        # Check file size
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
            )
        
        # Check file extension
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in self.allowed_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported audio format. Allowed formats: {', '.join(self.allowed_formats)}"
                )
        
        # Check MIME type
        allowed_mime_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav',
            'audio/m4a', 'audio/mp4', 'audio/aac', 'audio/flac',
            'audio/ogg', 'audio/vorbis'
        ]
        
        if file.content_type and file.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported MIME type: {file.content_type}"
            )
    
    async def _store_recording(
        self,
        user_id: str,
        recording_id: str,
        content: bytes,
        filename: str,
        metadata: Dict
    ) -> str:
        """Store recording in MinIO"""
        try:
            # Create storage path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            storage_path = f"{user_id}/recordings/{recording_id}/{timestamp}_{filename}"
            
            # Add legal metadata for storage
            storage_metadata = {
                "Content-Type": self._get_content_type(filename),
                "X-Recording-Type": metadata.get("recording_type", "legal_proceeding"),
                "X-Matter-Reference": metadata.get("matter_id", ""),
                "X-Recorded-By": metadata.get("recorded_by", user_id),
                "X-Duration-Seconds": str(metadata.get("duration_seconds", 0)),
                "X-Attendees": metadata.get("attendees", ""),
                "X-Upload-Time": datetime.utcnow().isoformat(),
                "X-Processing-Status": "completed"
            }
            
            # Upload to MinIO
            minio_service.client.put_object(
                bucket_name=settings.recordings_bucket,
                object_name=storage_path,
                data=io.BytesIO(content),
                length=len(content),
                metadata=storage_metadata
            )
            
            return storage_path
            
        except Exception as e:
            raise Exception(f"Failed to store recording: {str(e)}")
    
    async def _create_temp_file(self, content: bytes, filename: str) -> str:
        """Create temporary file for processing"""
        file_ext = os.path.splitext(filename)[1] if filename else '.m4a'
        
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_file.write(content)
            return temp_file.name
    
    async def _transcribe_recording(
        self,
        audio_path: str,
        metadata: Dict,
        recording_id: str
    ) -> Dict:
        """Transcribe recording using Whisper"""
        try:
            # Determine if we should use chunked transcription
            # (for recordings longer than 10 minutes)
            duration = metadata.get("duration_seconds", 0)
            use_chunked = duration > 600  # 10 minutes
            
            # Configure transcription options
            transcription_options = {
                "language": "en",  # Default to English, could be configurable
                "enable_timestamps": True,
                "legal_context": True
            }
            
            # Perform transcription
            if use_chunked:
                result = whisper_service.transcribe_chunked_audio(
                    audio_path,
                    chunk_duration=300,  # 5 minute chunks
                    overlap=30,  # 30 second overlap
                    **transcription_options
                )
            else:
                result = whisper_service.transcribe_audio(
                    audio_path,
                    **transcription_options
                )
            
            return result
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def _store_transcription(
        self,
        user_id: str,
        recording_id: str,
        transcription_result: Dict
    ) -> str:
        """Store transcription results in MinIO"""
        try:
            # Create transcription file path
            transcription_path = f"{user_id}/transcriptions/{recording_id}/transcript.txt"
            
            # Format transcription for storage
            transcript_content = f"""VERDICT360 LEGAL TRANSCRIPTION
Recording ID: {recording_id}
Processed: {transcription_result["metadata"]["timestamp"]}
Duration: {transcription_result["metadata"]["audio_duration"]:.1f} seconds
Model: {transcription_result["metadata"]["model_used"]}
Confidence: {transcription_result["confidence_score"]:.2f}
Word Count: {transcription_result["word_count"]}

LEGAL TERMS DETECTED:
{', '.join(transcription_result["legal_terms_detected"])}

FORMATTED TRANSCRIPT:
{transcription_result["formatted_transcript"]}

RAW TEXT:
{transcription_result["text"]}
"""
            
            # Upload transcription
            minio_service.client.put_object(
                bucket_name=settings.transcriptions_bucket,
                object_name=transcription_path,
                data=io.BytesIO(transcript_content.encode('utf-8')),
                length=len(transcript_content.encode('utf-8')),
                content_type="text/plain; charset=utf-8"
            )
            
            return transcription_path
            
        except Exception as e:
            raise Exception(f"Failed to store transcription: {str(e)}")
    
    async def _store_processing_results(
        self,
        user_id: str,
        recording_id: str,
        results: Dict
    ) -> str:
        """Store processing results as JSON"""
        try:
            results_path = f"{user_id}/processing-results/{recording_id}/audio_analysis.json"
            
            import json
            results_json = json.dumps(results, indent=2, default=str)
            
            minio_service.client.put_object(
                bucket_name=settings.recordings_bucket,
                object_name=results_path,
                data=io.BytesIO(results_json.encode('utf-8')),
                length=len(results_json.encode('utf-8')),
                content_type="application/json"
            )
            
            return results_path
            
        except Exception as e:
            raise Exception(f"Failed to store processing results: {str(e)}")
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename"""
        extension = filename.lower().split('.')[-1] if filename else ''
        content_types = {
            'm4a': 'audio/mp4',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'ogg': 'audio/ogg'
        }
        return content_types.get(extension, 'audio/mpeg')

# Global audio processor instance
audio_processor = AudioProcessor()
