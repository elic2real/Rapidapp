import asyncio
import hashlib
import json
import time
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.config import settings
from app.database import AsyncSessionLocal, SemanticCacheEntry
from app.cache import redis_client

logger = structlog.get_logger(__name__)


class SemanticCache:
    """Semantic cache for AI responses using embedding similarity."""

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the embedding model."""
        if self.initialized:
            return

        try:
            logger.info("Initializing semantic cache", model=settings.embedding_model)
            
            # Load in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: SentenceTransformer(settings.embedding_model)
            )
            
            self.initialized = True
            logger.info("Semantic cache initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize semantic cache", error=str(e))
            raise

    def _hash_prompt(self, prompt: str, model: str) -> str:
        """Create hash for prompt and model combination."""
        content = f"{prompt}:{model}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _encode_text(self, text: str) -> List[float]:
        """Encode text to embedding vector."""
        if not self.model:
            raise RuntimeError("Semantic cache not initialized")
        
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))

    async def get(
        self, 
        prompt: str, 
        model: str,
        similarity_threshold: Optional[float] = None
    ) -> Optional[Tuple[str, float]]:
        """
        Get cached response for prompt if similarity is above threshold.
        
        Returns:
            Tuple of (response, similarity_score) if found, None otherwise
        """
        if not settings.enable_semantic_cache or not self.initialized:
            return None

        threshold = similarity_threshold or settings.cache_similarity_threshold
        
        try:
            # First check exact hash match in Redis for speed
            prompt_hash = self._hash_prompt(prompt, model)
            redis_key = f"cache:exact:{prompt_hash}"
            
            cached_response = await redis_client.get(redis_key)
            if cached_response:
                logger.debug("Exact cache hit", prompt_hash=prompt_hash[:8])
                return cached_response, 1.0

            # Generate embedding for semantic search
            query_embedding = self._encode_text(prompt)
            
            # Search database for similar entries
            async with AsyncSessionLocal() as session:
                # Get candidates from database
                result = await session.execute(
                    select(SemanticCacheEntry)
                    .where(SemanticCacheEntry.model_name == model)
                    .order_by(SemanticCacheEntry.last_accessed.desc())
                    .limit(100)  # Limit search space for performance
                )
                
                candidates = result.scalars().all()
                
                best_match = None
                best_similarity = 0.0
                
                # Calculate similarities
                for candidate in candidates:
                    similarity = self._cosine_similarity(
                        query_embedding, 
                        candidate.embedding
                    )
                    
                    if similarity > best_similarity and similarity >= threshold:
                        best_similarity = similarity
                        best_match = candidate

                if best_match:
                    # Update access statistics
                    best_match.hit_count += 1
                    best_match.last_accessed = func.now()
                    await session.commit()
                    
                    # Cache exact match in Redis for future speed
                    await redis_client.setex(
                        redis_key,
                        settings.cache_ttl_seconds,
                        best_match.response
                    )
                    
                    logger.info(
                        "Semantic cache hit",
                        similarity=best_similarity,
                        hit_count=best_match.hit_count,
                        prompt_hash=prompt_hash[:8]
                    )
                    
                    return best_match.response, best_similarity

                logger.debug(
                    "Semantic cache miss",
                    best_similarity=best_similarity,
                    threshold=threshold,
                    candidates_checked=len(candidates)
                )
                
                return None

        except Exception as e:
            logger.error("Error in semantic cache get", error=str(e))
            return None

    async def set(
        self, 
        prompt: str, 
        model: str, 
        response: str,
        tokens_used: Optional[int] = None
    ) -> None:
        """Cache response for prompt."""
        if not settings.enable_semantic_cache or not self.initialized:
            return

        try:
            prompt_hash = self._hash_prompt(prompt, model)
            embedding = self._encode_text(prompt)
            
            # Store in database
            async with AsyncSessionLocal() as session:
                # Check if entry already exists
                existing = await session.execute(
                    select(SemanticCacheEntry)
                    .where(SemanticCacheEntry.prompt_hash == prompt_hash)
                )
                
                if existing.scalars().first():
                    logger.debug("Cache entry already exists", prompt_hash=prompt_hash[:8])
                    return

                # Create new entry
                cache_entry = SemanticCacheEntry(
                    prompt_hash=prompt_hash,
                    prompt_text=prompt,
                    embedding=embedding,
                    response=response,
                    model_name=model,
                    tokens_used=tokens_used,
                )
                
                session.add(cache_entry)
                await session.commit()

            # Also cache exact match in Redis
            redis_key = f"cache:exact:{prompt_hash}"
            await redis_client.setex(
                redis_key,
                settings.cache_ttl_seconds,
                response
            )
            
            logger.info("Cached response", prompt_hash=prompt_hash[:8], model=model)
            
            # Cleanup old entries if needed
            await self._cleanup_if_needed()
            
        except Exception as e:
            logger.error("Error caching response", error=str(e))

    async def search(
        self, 
        query: str, 
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search cache entries by semantic similarity."""
        if not self.initialized:
            return []

        try:
            query_embedding = self._encode_text(query)
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(SemanticCacheEntry)
                    .order_by(SemanticCacheEntry.created_at.desc())
                    .limit(500)  # Reasonable search space
                )
                
                candidates = result.scalars().all()
                results = []
                
                for candidate in candidates:
                    similarity = self._cosine_similarity(
                        query_embedding,
                        candidate.embedding
                    )
                    
                    if similarity >= similarity_threshold:
                        results.append({
                            "text": candidate.prompt_text,
                            "response": candidate.response,
                            "similarity_score": similarity,
                            "model": candidate.model_name,
                            "hit_count": candidate.hit_count,
                            "created_at": candidate.created_at,
                            "last_accessed": candidate.last_accessed,
                        })
                
                # Sort by similarity and limit
                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                return results[:limit]
                
        except Exception as e:
            logger.error("Error searching cache", error=str(e))
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            async with AsyncSessionLocal() as session:
                # Total entries
                total_result = await session.execute(
                    select(func.count(SemanticCacheEntry.id))
                )
                total_entries = total_result.scalar() or 0
                
                # Average hit count
                hit_result = await session.execute(
                    select(func.avg(SemanticCacheEntry.hit_count))
                )
                avg_hit_count = hit_result.scalar() or 0
                
                # Redis cache stats
                redis_info = await redis_client.info()
                redis_memory_mb = redis_info.get('used_memory', 0) / (1024 * 1024)
                
                return {
                    "total_entries": total_entries,
                    "avg_hit_count": float(avg_hit_count),
                    "redis_memory_mb": redis_memory_mb,
                    "embedding_model": settings.embedding_model,
                    "similarity_threshold": settings.cache_similarity_threshold,
                    "max_entries": settings.max_cache_entries,
                }
                
        except Exception as e:
            logger.error("Error getting cache stats", error=str(e))
            return {}

    async def clear(self) -> int:
        """Clear all cache entries."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    delete(SemanticCacheEntry)
                )
                deleted_count = result.rowcount
                await session.commit()
                
            # Clear Redis cache
            keys = await redis_client.keys("cache:exact:*")
            if keys:
                await redis_client.delete(*keys)
                
            logger.info("Cache cleared", deleted_count=deleted_count)
            return deleted_count
            
        except Exception as e:
            logger.error("Error clearing cache", error=str(e))
            return 0

    async def _cleanup_if_needed(self) -> None:
        """Clean up old cache entries if limit exceeded."""
        try:
            async with AsyncSessionLocal() as session:
                count_result = await session.execute(
                    select(func.count(SemanticCacheEntry.id))
                )
                total_count = count_result.scalar() or 0
                
                if total_count > settings.max_cache_entries:
                    # Delete oldest entries
                    entries_to_delete = total_count - settings.max_cache_entries + 1000
                    
                    oldest_entries = await session.execute(
                        select(SemanticCacheEntry.id)
                        .order_by(SemanticCacheEntry.last_accessed.asc())
                        .limit(entries_to_delete)
                    )
                    
                    ids_to_delete = [row[0] for row in oldest_entries]
                    
                    if ids_to_delete:
                        await session.execute(
                            delete(SemanticCacheEntry)
                            .where(SemanticCacheEntry.id.in_(ids_to_delete))
                        )
                        await session.commit()
                        
                        logger.info(
                            "Cleaned up old cache entries",
                            deleted_count=len(ids_to_delete)
                        )
                        
        except Exception as e:
            logger.error("Error in cache cleanup", error=str(e))


# Global semantic cache instance
semantic_cache = SemanticCache()
