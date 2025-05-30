from minio import Minio
from minio.error import S3Error
import io
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings

class MinIOService:
    """MinIO storage service for legal documents"""
    
    def __init__(self):
        self.client = Minio(
            f"{settings.minio_endpoint}:{settings.minio_port}",
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        
    async def ensure_buckets_exist(self):
        """Ensure all required buckets exist"""
        buckets = [
            settings.documents_bucket,
            settings.recordings_bucket,
            settings.transcriptions_bucket
        ]
        
        for bucket_name in buckets:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    print(f"✅ Created bucket: {bucket_name}")
                else:
                    print(f"✅ Bucket exists: {bucket_name}")
            except S3Error as e:
                print(f"❌ Error with bucket {bucket_name}: {e}")
                raise
    
    def upload_document(
        self, 
        user_id: str, 
        document_id: str, 
        file_content: bytes, 
        filename: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Upload document to MinIO with legal metadata
        Returns the object path
        """
        try:
            # Create object path: user_id/documents/document_id/filename
            object_path = f"{user_id}/documents/{document_id}/{filename}"
            
            # Add legal compliance metadata
            object_metadata = {
                "Content-Type": self._get_content_type(filename),
                "X-Legal-Matter": metadata.get("matter_id", "unassigned"),
                "X-Document-Type": metadata.get("document_type", "legal_document"),
                "X-Jurisdiction": metadata.get("jurisdiction", "South Africa"),
                "X-Created-By": user_id,
                "X-Upload-Time": datetime.utcnow().isoformat(),
                "X-Document-Title": metadata.get("title", ""),
                "X-Processing-Status": "completed"
            }
            
            # Upload to MinIO
            result = self.client.put_object(
                bucket_name=settings.documents_bucket,
                object_name=object_path,
                data=io.BytesIO(file_content),
                length=len(file_content),
                metadata=object_metadata
            )
            
            print(f"✅ Document uploaded to MinIO: {object_path}")
            return object_path
            
        except S3Error as e:
            print(f"❌ MinIO upload error: {e}")
            raise Exception(f"Failed to upload document to storage: {str(e)}")
    
    def upload_processing_result(
        self,
        user_id: str,
        document_id: str,
        processing_result: Dict[str, Any]
    ) -> str:
        """Upload document processing results as JSON"""
        try:
            # Create path for processing results
            object_path = f"{user_id}/processing-results/{document_id}/analysis.json"
            
            # Convert processing result to JSON
            json_content = json.dumps(processing_result, indent=2, default=str)
            json_bytes = json_content.encode('utf-8')
            
            # Upload processing results
            result = self.client.put_object(
                bucket_name=settings.documents_bucket,
                object_name=object_path,
                data=io.BytesIO(json_bytes),
                length=len(json_bytes),
                content_type="application/json"
            )
            
            print(f"✅ Processing results uploaded: {object_path}")
            return object_path
            
        except S3Error as e:
            print(f"❌ Failed to upload processing results: {e}")
            raise Exception(f"Failed to store processing results: {str(e)}")
    
    def get_download_url(self, object_path: str, expiry_hours: int = 24) -> str:
        """Generate presigned download URL"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=settings.documents_bucket,
                object_name=object_path,
                expires=timedelta(hours=expiry_hours)
            )
            return url
        except S3Error as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename"""
        extension = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'txt': 'text/plain'
        }
        return content_types.get(extension, 'application/octet-stream')

# Global MinIO service instance
minio_service = MinIOService()
