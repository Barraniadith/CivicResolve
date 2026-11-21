"""
Centralized Configuration & Application Settings for CivicResolve.
Provides typed, validated configuration parameters for AI models, databases, and API limits.
"""
import os
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    app_name: str = "CivicResolve"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    max_pagination_limit: int = 500
    default_pagination_limit: int = 100
    cache_ttl_seconds: int = 10
    coimbatore_center_lat: float = 11.0168
    coimbatore_center_lng: float = 76.9558

settings = AppConfig()
