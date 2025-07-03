"""
Configuration settings for Verdict360 Legal Intelligence API
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8001, env="API_PORT")
    API_DEBUG: bool = Field(default=True, env="API_DEBUG")
    
    
    # Vector Database Configuration
    CHROMA_DB_PATH: str = Field(default="./chroma_db", env="CHROMA_DB_PATH")
    CHROMA_COLLECTION_NAME: str = Field(default="legal_documents", env="CHROMA_COLLECTION_NAME")
    
    # Embedding Model Configuration
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DEVICE: str = Field(default="cpu", env="EMBEDDING_DEVICE")
    
    # Document Processing
    MAX_CHUNK_SIZE: int = Field(default=1000, env="MAX_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    MAX_SEARCH_RESULTS: int = Field(default=20, env="MAX_SEARCH_RESULTS")
    
    # South African Legal Configuration
    DEFAULT_JURISDICTION: str = Field(default="South Africa", env="DEFAULT_JURISDICTION")
    LEGAL_CITATION_PATTERNS_ENABLED: bool = Field(default=True, env="LEGAL_CITATION_PATTERNS_ENABLED")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Additional settings that may be in .env
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="", env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    
    # Database Configuration with defaults
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://Verdict360:devpassword@localhost:5432/Verdict360", 
        env="DATABASE_URL"
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields

# Create global settings instance
settings = Settings()
