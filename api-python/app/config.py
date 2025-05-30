import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Settings class using environment variables only"""
    
    # MinIO Configuration - all from environment variables
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT")
    minio_port: int = int(os.getenv("MINIO_PORT", "9000"))
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY") 
    minio_secure: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
    
    # Bucket names from environment
    documents_bucket: str = os.getenv("MINIO_BUCKET_DOCUMENTS")
    recordings_bucket: str = os.getenv("MINIO_BUCKET_RECORDINGS")
    transcriptions_bucket: str = os.getenv("MINIO_BUCKET_TRANSCRIPTIONS")
    
    def __post_init__(self):
        """Validate that required environment variables are set"""
        required_vars = [
            "MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY",
            "MINIO_BUCKET_DOCUMENTS", "MINIO_BUCKET_RECORDINGS", "MINIO_BUCKET_TRANSCRIPTIONS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def debug_config(self):
        """Print configuration for debugging (without exposing secrets)"""
        print(f"🔑 MinIO Endpoint: {self.minio_endpoint}:{self.minio_port}")
        print(f"🔑 MinIO User: {self.minio_access_key}")
        print(f"🔑 MinIO Password: {'*' * len(self.minio_secret_key) if self.minio_secret_key else 'NOT SET'}")
        print(f"📦 Buckets: {self.documents_bucket}, {self.recordings_bucket}, {self.transcriptions_bucket}")

settings = Settings()

# Validate configuration on import
try:
    settings.__post_init__()
    settings.debug_config()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("⚠️  Please check your .env file")
