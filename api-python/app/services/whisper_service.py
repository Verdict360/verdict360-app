import whisper
import torch
import os
import tempfile
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import librosa
import soundfile as sf
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class WhisperTranscriptionService:
    """
    Self-hosted Whisper transcription service for legal audio recordings
    Optimized for South African English and legal terminology
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper service
        
        Model sizes available:
        - tiny: Fastest, least accurate (~1GB VRAM)
        - base: Good balance (~1GB VRAM) 
        - small: Better accuracy (~2GB VRAM)
        - medium: High accuracy (~5GB VRAM)
        - large: Best accuracy (~10GB VRAM)
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Legal-specific vocabulary for better transcription
        self.legal_vocabulary = [
            "magistrate", "constitutional court", "high court", "supreme court of appeal",
            "plaintiff", "defendant", "appellant", "respondent", "matter", "judgment",
            "section", "subsection", "regulation", "act", "statute", "constitution",
            "advocate", "attorney", "counsel", "silk", "chambers", "clerk",
            "affidavit", "pleading", "discovery", "subpoena", "summons", "writ",
            "interim", "interdict", "injunction", "mandamus", "certiorari",
            "rand", "cents", "rands", "johannesburg", "cape town", "durban", "pretoria",
            "gauteng", "western cape", "kwazulu-natal", "eastern cape", "free state",
            "limpopo", "mpumalanga", "north west", "northern cape"
        ]
        
        logger.info(f"Whisper service initialized with {model_size} model on {self.device}")
    
    def load_model(self) -> None:
        """Load the Whisper model (done lazily to save memory)"""
        if self.model is None:
            logger.info(f"Loading Whisper {self.model_size} model...")
            try:
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info(f"Whisper model loaded successfully on {self.device}")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise Exception(f"Could not load Whisper model: {str(e)}")
    
    def preprocess_audio(self, audio_path: str) -> str:
        """
        Preprocess audio for optimal Whisper transcription
        - Convert to WAV format
        - Normalize audio levels  
        - Remove silence
        - Optimize for speech
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)
            
            # Convert to mono if stereo (Whisper works better with mono)
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate to 16kHz (Whisper's native rate)
            audio = audio.set_frame_rate(16000)
            
            # Normalize audio (legal recordings can have varying volumes)
            audio = audio.normalize()
            
            # Remove silence from beginning and end
            audio = audio.strip_silence(silence_len=1000, silence_thresh=-50)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                audio.export(temp_file.name, format="wav")
                return temp_file.name
                
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise Exception(f"Could not preprocess audio: {str(e)}")
    
    def transcribe_audio(
        self, 
        audio_path: str, 
        language: str = "en",
        enable_timestamps: bool = True,
        legal_context: bool = True
    ) -> Dict:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code (en for English, af for Afrikaans, etc.)
            enable_timestamps: Include word-level timestamps
            legal_context: Apply legal vocabulary optimization
            
        Returns:
            Dict with transcription text, segments, and metadata
        """
        try:
            # Load model if not already loaded
            self.load_model()
            
            # Preprocess audio for better results
            processed_audio_path = self.preprocess_audio(audio_path)
            
            try:
                logger.info(f"Starting transcription of {audio_path}")
                start_time = datetime.now()
                
                # Configure transcription options
                options = {
                    "language": language,
                    "task": "transcribe",
                    "verbose": False,
                    "word_timestamps": enable_timestamps,
                }
                
                # Add legal vocabulary as initial prompt to improve accuracy
                if legal_context:
                    legal_prompt = " ".join(self.legal_vocabulary[:50])  # Use first 50 terms
                    options["initial_prompt"] = f"Legal proceeding transcript: {legal_prompt}"
                
                # Perform transcription
                result = self.model.transcribe(processed_audio_path, **options)
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Format segments with timestamps
                formatted_segments = []
                for segment in result.get("segments", []):
                    formatted_segments.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"].strip(),
                        "confidence": segment.get("avg_logprob", 0.0)
                    })
                
                # Create formatted transcript with timestamps
                formatted_transcript = self._format_transcript_with_timestamps(formatted_segments)
                
                # Detect legal terminology used
                legal_terms_found = self._detect_legal_terminology(result["text"])
                
                transcription_result = {
                    "text": result["text"],
                    "formatted_transcript": formatted_transcript,
                    "segments": formatted_segments,
                    "language": result["language"],
                    "processing_time_seconds": processing_time,
                    "legal_terms_detected": legal_terms_found,
                    "word_count": len(result["text"].split()),
                    "confidence_score": self._calculate_average_confidence(formatted_segments),
                    "metadata": {
                        "model_used": self.model_size,
                        "device": self.device,
                        "timestamp": datetime.now().isoformat(),
                        "audio_duration": result.get("duration", 0)
                    }
                }
                
                logger.info(f"Transcription completed in {processing_time:.2f} seconds")
                return transcription_result
                
            finally:
                # Clean up preprocessed file
                if os.path.exists(processed_audio_path):
                    os.unlink(processed_audio_path)
                    
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def transcribe_chunked_audio(
        self, 
        audio_path: str, 
        chunk_duration: int = 300,  # 5 minutes
        overlap: int = 30,  # 30 seconds overlap
        **kwargs
    ) -> Dict:
        """
        Transcribe long audio files by splitting into chunks
        Useful for lengthy legal proceedings
        """
        try:
            # Load audio to get duration
            audio = AudioSegment.from_file(audio_path)
            total_duration = len(audio) / 1000.0  # Convert to seconds
            
            if total_duration <= chunk_duration:
                # File is short enough, transcribe normally
                return self.transcribe_audio(audio_path, **kwargs)
            
            logger.info(f"Chunking {total_duration:.1f}s audio into {chunk_duration}s segments")
            
            chunks = []
            all_segments = []
            full_text = ""
            
            # Split audio into overlapping chunks
            for start_time in range(0, int(total_duration), chunk_duration - overlap):
                end_time = min(start_time + chunk_duration, total_duration)
                
                # Extract chunk
                start_ms = start_time * 1000
                end_ms = end_time * 1000
                chunk_audio = audio[start_ms:end_ms]
                
                # Save chunk to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    chunk_audio.export(temp_file.name, format="wav")
                    chunk_path = temp_file.name
                
                try:
                    # Transcribe chunk
                    chunk_result = self.transcribe_audio(chunk_path, **kwargs)
                    
                    # Adjust timestamps to global time
                    adjusted_segments = []
                    for segment in chunk_result["segments"]:
                        adjusted_segment = segment.copy()
                        adjusted_segment["start"] += start_time
                        adjusted_segment["end"] += start_time
                        adjusted_segments.append(adjusted_segment)
                    
                    all_segments.extend(adjusted_segments)
                    chunks.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "text": chunk_result["text"],
                        "word_count": chunk_result["word_count"]
                    })
                    
                    full_text += " " + chunk_result["text"]
                    
                finally:
                    # Clean up chunk file
                    if os.path.exists(chunk_path):
                        os.unlink(chunk_path)
            
            # Create formatted transcript
            formatted_transcript = self._format_transcript_with_timestamps(all_segments)
            
            return {
                "text": full_text.strip(),
                "formatted_transcript": formatted_transcript,
                "segments": all_segments,
                "chunks": chunks,
                "total_duration": total_duration,
                "chunk_count": len(chunks),
                "language": kwargs.get("language", "en"),
                "legal_terms_detected": self._detect_legal_terminology(full_text),
                "word_count": len(full_text.split()),
                "confidence_score": self._calculate_average_confidence(all_segments),
                "metadata": {
                    "model_used": self.model_size,
                    "device": self.device,
                    "timestamp": datetime.now().isoformat(),
                    "chunked": True,
                    "chunk_duration": chunk_duration,
                    "overlap": overlap
                }
            }
            
        except Exception as e:
            logger.error(f"Chunked transcription failed: {e}")
            raise Exception(f"Chunked transcription failed: {str(e)}")
    
    def _format_transcript_with_timestamps(self, segments: List[Dict]) -> str:
        """Format transcript with timestamps for legal review"""
        formatted_lines = []
        
        for segment in segments:
            start_time = self._format_timestamp(segment["start"])
            end_time = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            formatted_lines.append(f"[{start_time} - {end_time}] {text}")
        
        return "\n\n".join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _detect_legal_terminology(self, text: str) -> List[str]:
        """Detect legal terms in transcribed text"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.legal_vocabulary:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _calculate_average_confidence(self, segments: List[Dict]) -> float:
        """Calculate average confidence across all segments"""
        if not segments:
            return 0.0
        
        confidences = [seg.get("confidence", 0.0) for seg in segments]
        return sum(confidences) / len(confidences)
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of languages supported by Whisper"""
        return [
            {"code": "en", "name": "English"},
            {"code": "af", "name": "Afrikaans"},
            {"code": "zu", "name": "Zulu"},
            {"code": "xh", "name": "Xhosa"},
            {"code": "st", "name": "Sesotho"},
            {"code": "tn", "name": "Setswana"},
            {"code": "ve", "name": "Venda"},
            {"code": "ts", "name": "Tsonga"},
            {"code": "ss", "name": "Siswati"},
            {"code": "nr", "name": "Ndebele"},
            {"code": "nso", "name": "Northern Sotho"},
        ]
    
    def health_check(self) -> Dict[str, any]:
        """Check if Whisper service is healthy"""
        try:
            return {
                "status": "healthy",
                "model_size": self.model_size,
                "device": self.device,
                "model_loaded": self.model is not None,
                "cuda_available": torch.cuda.is_available(),
                "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else "N/A"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global Whisper service instance
whisper_service = WhisperTranscriptionService(model_size="base")
