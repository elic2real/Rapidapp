import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server configuration
    port: int = Field(default=8001, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    development: bool = Field(default=False, description="Development mode")
    log_level: str = Field(default="INFO", description="Log level")

    # Database configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/polished_manual",
        description="Database connection URL"
    )

    # Redis configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )

    # AI Model configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server base URL"
    )
    
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional)"
    )
    
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key (optional)"
    )

    # Model routing configuration
    default_model: str = Field(
        default="llama3:8b",
        description="Default model for requests"
    )
    
    prefer_local_models: bool = Field(
        default=True,
        description="Prefer local models over cloud APIs"
    )
    
    max_tokens_local: int = Field(
        default=4096,
        description="Max tokens for local models"
    )
    
    max_tokens_cloud: int = Field(
        default=8192,
        description="Max tokens for cloud models"
    )

    # Semantic cache configuration
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Model for generating embeddings"
    )
    
    cache_similarity_threshold: float = Field(
        default=0.85,
        description="Similarity threshold for cache hits"
    )
    
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache TTL in seconds"
    )
    
    max_cache_entries: int = Field(
        default=10000,
        description="Maximum number of cache entries"
    )

    # Rate limiting
    rate_limit_requests_per_minute: int = Field(
        default=100,
        description="Rate limit per client per minute"
    )

    # Telemetry configuration
    jaeger_endpoint: str = Field(
        default="http://localhost:14268/api/traces",
        description="Jaeger tracing endpoint"
    )
    
    enable_telemetry: bool = Field(
        default=True,
        description="Enable OpenTelemetry tracing"
    )

    # Security
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (optional)"
    )

    # Performance tuning
    max_concurrent_requests: int = Field(
        default=50,
        description="Maximum concurrent requests"
    )
    
    request_timeout_seconds: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    model_load_timeout_seconds: int = Field(
        default=120,
        description="Model loading timeout in seconds"
    )

    # Feature flags
    enable_semantic_cache: bool = Field(
        default=True,
        description="Enable semantic caching"
    )
    
    enable_model_fallback: bool = Field(
        default=True,
        description="Enable model fallback on errors"
    )
    
    enable_request_batching: bool = Field(
        default=False,
        description="Enable request batching"
    )
    
    enable_streaming: bool = Field(
        default=True,
        description="Enable streaming responses"
    )


# Global settings instance
settings = Settings()
