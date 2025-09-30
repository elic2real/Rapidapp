from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class CompletionRequest(BaseModel):
    """Request for text completion."""
    prompt: str = Field(..., description="Input prompt")
    model: Optional[str] = Field(default=None, description="Model to use (optional)")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(default=False, description="Stream response")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Request metadata")


class ChatRequest(BaseModel):
    """Request for chat completion."""
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    model: Optional[str] = Field(default=None, description="Model to use (optional)")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(default=False, description="Stream response")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Request metadata")


class CompletionResponse(BaseModel):
    """Response for text completion."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Response ID")
    text: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Model provider")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    cache_hit: bool = Field(default=False, description="Whether response came from cache")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ChatResponse(BaseModel):
    """Response for chat completion."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Response ID")
    message: ChatMessage = Field(..., description="Assistant's response message")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Model provider")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    cache_hit: bool = Field(default=False, description="Whether response came from cache")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    id: str = Field(..., description="Response ID")
    delta: str = Field(..., description="Text delta")
    finished: bool = Field(default=False, description="Whether stream is finished")


class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Model provider")
    max_tokens: int = Field(..., description="Maximum context length")
    available: bool = Field(..., description="Whether model is currently available")
    estimated_latency_ms: Optional[int] = Field(default=None, description="Estimated latency")
    cost_per_token: Optional[float] = Field(default=None, description="Cost per token (if applicable)")


class CacheStats(BaseModel):
    """Cache statistics."""
    total_entries: int = Field(..., description="Total cache entries")
    hit_rate: float = Field(..., description="Cache hit rate")
    total_hits: int = Field(..., description="Total cache hits")
    total_misses: int = Field(..., description="Total cache misses")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    avg_similarity_score: float = Field(..., description="Average similarity score for hits")


class HealthStatus(BaseModel):
    """Health check status."""
    status: str = Field(..., description="Overall status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    services: Dict[str, bool] = Field(..., description="Individual service statuses")
    models: List[ModelInfo] = Field(default_factory=list, description="Available models")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class SemanticCacheQuery(BaseModel):
    """Semantic cache query."""
    text: str = Field(..., description="Text to search for")
    similarity_threshold: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Similarity threshold (0-1)"
    )
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return")


class SemanticCacheResult(BaseModel):
    """Semantic cache search result."""
    text: str = Field(..., description="Cached text")
    response: str = Field(..., description="Cached response")
    similarity_score: float = Field(..., description="Similarity score")
    model: str = Field(..., description="Model used")
    hit_count: int = Field(..., description="Number of times this cache entry was used")
    created_at: datetime = Field(..., description="Cache entry creation time")
    last_accessed: datetime = Field(..., description="Last access time")
