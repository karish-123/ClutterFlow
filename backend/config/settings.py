# backend/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    database_url: str
    
    # Application
    max_file_size: int = 52428800  # 50MB
    temp_dir: str = "temp"
    environment: str = "development"
    
    # API
    api_title: str = "Digital Clutter Cleaner API"
    api_version: str = "1.0.0"
    
    # LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b"
    ollama_timeout: int = 60
    max_tokens: int = 2000
    
    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Processing Settings
    max_chunk_size: int = 2000
    max_summary_length: int = 500
    background_processing_enabled: bool = True
    max_retry_attempts: int = 3
    
    # Feature Flags
    enable_summarization: bool = True
    enable_classification: bool = True
    enable_semantic_search: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()