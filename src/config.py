"""
Configuration management
"""

import os
from typing import Dict, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Model Configuration
    model_name: str = "unitary/toxic-bert"
    model_cache_dir: str = "./models"
    device: str = "cpu"  # or "cuda" if available
    
    # Detection Thresholds
    default_threshold: float = 0.5
    block_threshold: float = 0.8
    flag_threshold: float = 0.5
    
    # Language Detection
    supported_languages: List[str] = [
        "en", "hi", "bn", "ta", "te", "kn", "ml", "gu", "pa", "or", "ur"
    ]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Redis Configuration (for caching and rate limiting)
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = False
    
    # Lexicon Configuration
    lexicon_dir: str = "./lexicons"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_prefix = "ABUSE_API_"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()