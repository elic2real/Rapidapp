import asyncio
import time
from typing import Dict, List, Optional, Protocol, AsyncGenerator
from abc import ABC, abstractmethod
import httpx
import structlog

from app.config import settings
from app.models import CompletionRequest, ChatRequest, CompletionResponse, ChatResponse, ModelInfo

logger = structlog.get_logger(__name__)


class ModelProvider(Protocol):
    """Protocol for AI model providers."""
    
    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate text completion."""
        pass
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    async def stream_complete(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream text completion."""
        pass
    
    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Stream chat completion."""
        pass
    
    @abstractmethod
    async def get_models(self) -> List[ModelInfo]:
        """Get available models."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        pass


class OllamaProvider:
    """Ollama local model provider."""
    
    def __init__(self, base_url: str = settings.ollama_base_url):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=settings.request_timeout_seconds)
        self.name = "ollama"
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate text completion using Ollama."""
        start_time = time.time()
        
        model = request.model or settings.default_model
        
        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": False,
        }
        
        if request.max_tokens:
            payload["options"] = {"num_predict": request.max_tokens}
        if request.temperature is not None:
            payload.setdefault("options", {})["temperature"] = request.temperature
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return CompletionResponse(
                text=data["response"],
                model=model,
                provider=self.name,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                processing_time_ms=processing_time
            )
            
        except httpx.RequestError as e:
            logger.error("Ollama request failed", error=str(e))
            raise RuntimeError(f"Ollama request failed: {e}")
        except httpx.HTTPStatusError as e:
            logger.error("Ollama HTTP error", status_code=e.response.status_code, error=str(e))
            raise RuntimeError(f"Ollama HTTP error: {e.response.status_code}")
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Generate chat completion using Ollama."""
        start_time = time.time()
        
        model = request.model or settings.default_model
        
        # Convert messages to Ollama format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        
        if request.max_tokens:
            payload["options"] = {"num_predict": request.max_tokens}
        if request.temperature is not None:
            payload.setdefault("options", {})["temperature"] = request.temperature
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            processing_time = int((time.time() - start_time) * 1000)
            
            from app.models import ChatMessage
            
            return ChatResponse(
                message=ChatMessage(
                    role="assistant",
                    content=data["message"]["content"]
                ),
                model=model,
                provider=self.name,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                processing_time_ms=processing_time
            )
            
        except httpx.RequestError as e:
            logger.error("Ollama request failed", error=str(e))
            raise RuntimeError(f"Ollama request failed: {e}")
        except httpx.HTTPStatusError as e:
            logger.error("Ollama HTTP error", status_code=e.response.status_code, error=str(e))
            raise RuntimeError(f"Ollama HTTP error: {e.response.status_code}")
    
    async def stream_complete(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream text completion using Ollama."""
        model = request.model or settings.default_model
        
        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": True,
        }
        
        if request.max_tokens:
            payload["options"] = {"num_predict": request.max_tokens}
        if request.temperature is not None:
            payload.setdefault("options", {})["temperature"] = request.temperature
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done"):
                            break
                            
        except Exception as e:
            logger.error("Ollama streaming failed", error=str(e))
            raise RuntimeError(f"Ollama streaming failed: {e}")
    
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Stream chat completion using Ollama."""
        model = request.model or settings.default_model
        
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        
        if request.max_tokens:
            payload["options"] = {"num_predict": request.max_tokens}
        if request.temperature is not None:
            payload.setdefault("options", {})["temperature"] = request.temperature
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        if data.get("done"):
                            break
                            
        except Exception as e:
            logger.error("Ollama streaming failed", error=str(e))
            raise RuntimeError(f"Ollama streaming failed: {e}")
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available Ollama models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append(ModelInfo(
                    name=model["name"],
                    provider=self.name,
                    max_tokens=settings.max_tokens_local,
                    available=True,
                    estimated_latency_ms=100,  # Estimate for local models
                    cost_per_token=0.0  # Local models are free
                ))
            
            return models
            
        except Exception as e:
            logger.error("Failed to get Ollama models", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        """Check Ollama health."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False


class OpenAIProvider:
    """OpenAI cloud provider."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.client = httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.name = "openai"
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate text completion using OpenAI."""
        start_time = time.time()
        
        model = request.model or "gpt-3.5-turbo-instruct"
        
        payload = {
            "model": model,
            "prompt": request.prompt,
            "max_tokens": request.max_tokens or settings.max_tokens_cloud,
            "temperature": request.temperature or 0.7,
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return CompletionResponse(
                text=data["choices"][0]["text"],
                model=model,
                provider=self.name,
                usage=data["usage"],
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("OpenAI request failed", error=str(e))
            raise RuntimeError(f"OpenAI request failed: {e}")
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Generate chat completion using OpenAI."""
        start_time = time.time()
        
        model = request.model or "gpt-3.5-turbo"
        
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or settings.max_tokens_cloud,
            "temperature": request.temperature or 0.7,
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            processing_time = int((time.time() - start_time) * 1000)
            
            from app.models import ChatMessage
            
            return ChatResponse(
                message=ChatMessage(
                    role="assistant",
                    content=data["choices"][0]["message"]["content"]
                ),
                model=model,
                provider=self.name,
                usage=data["usage"],
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("OpenAI request failed", error=str(e))
            raise RuntimeError(f"OpenAI request failed: {e}")
    
    async def stream_complete(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream text completion using OpenAI."""
        # Implementation for OpenAI streaming
        model = request.model or "gpt-3.5-turbo-instruct"
        
        payload = {
            "model": model,
            "prompt": request.prompt,
            "max_tokens": request.max_tokens or settings.max_tokens_cloud,
            "temperature": request.temperature or 0.7,
            "stream": True,
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                yield data["choices"][0].get("text", "")
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error("OpenAI streaming failed", error=str(e))
            raise RuntimeError(f"OpenAI streaming failed: {e}")
    
    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Stream chat completion using OpenAI."""
        # Similar to stream_complete but for chat
        model = request.model or "gpt-3.5-turbo"
        
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or settings.max_tokens_cloud,
            "temperature": request.temperature or 0.7,
            "stream": True,
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error("OpenAI streaming failed", error=str(e))
            raise RuntimeError(f"OpenAI streaming failed: {e}")
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available OpenAI models."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            
            # Filter to chat and completion models
            relevant_models = [
                model for model in data.get("data", [])
                if any(prefix in model["id"] for prefix in ["gpt-", "text-"])
            ]
            
            models = []
            for model in relevant_models:
                models.append(ModelInfo(
                    name=model["id"],
                    provider=self.name,
                    max_tokens=settings.max_tokens_cloud,
                    available=True,
                    estimated_latency_ms=500,  # Estimate for cloud models
                    cost_per_token=0.002  # Rough estimate
                ))
            
            return models
            
        except Exception as e:
            logger.error("Failed to get OpenAI models", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        """Check OpenAI health."""
        try:
            response = await self.client.get(f"{self.base_url}/models", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False


class ModelManager:
    """Manages AI model providers and routing."""
    
    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.model_cache: Dict[str, List[ModelInfo]] = {}
        self.last_health_check = 0
        self.health_status: Dict[str, bool] = {}
    
    async def initialize(self) -> None:
        """Initialize available providers."""
        logger.info("Initializing model providers")
        
        # Always add Ollama provider
        self.providers["ollama"] = OllamaProvider()
        
        # Add OpenAI if API key is provided
        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(settings.openai_api_key)
        
        # TODO: Add Anthropic provider
        
        # Initial health check
        await self._update_health_status()
        
        logger.info("Model providers initialized", providers=list(self.providers.keys()))
    
    async def get_best_provider(self, model: Optional[str] = None) -> ModelProvider:
        """Get the best available provider for a model."""
        if not self.providers:
            raise RuntimeError("No providers available")
        
        # Update health status periodically
        current_time = time.time()
        if current_time - self.last_health_check > 60:  # Check every minute
            await self._update_health_status()
        
        # If specific model requested, try to route appropriately
        if model:
            # Local models (Ollama)
            if any(model.startswith(prefix) for prefix in ["llama", "mistral", "codellama"]):
                if "ollama" in self.providers and self.health_status.get("ollama", False):
                    return self.providers["ollama"]
            
            # OpenAI models
            if model.startswith("gpt-") or model.startswith("text-"):
                if "openai" in self.providers and self.health_status.get("openai", False):
                    return self.providers["openai"]
        
        # Default routing based on preferences
        if settings.prefer_local_models:
            # Try local providers first
            if "ollama" in self.providers and self.health_status.get("ollama", False):
                return self.providers["ollama"]
            
            # Fall back to cloud providers
            if "openai" in self.providers and self.health_status.get("openai", False):
                return self.providers["openai"]
        else:
            # Try cloud providers first
            if "openai" in self.providers and self.health_status.get("openai", False):
                return self.providers["openai"]
            
            # Fall back to local providers
            if "ollama" in self.providers and self.health_status.get("ollama", False):
                return self.providers["ollama"]
        
        # Return any available provider as last resort
        for name, provider in self.providers.items():
            if self.health_status.get(name, False):
                return provider
        
        raise RuntimeError("No healthy providers available")
    
    async def get_all_models(self, force_refresh: bool = False) -> List[ModelInfo]:
        """Get all available models from all providers."""
        if not force_refresh and self.model_cache:
            # Return cached models
            all_models = []
            for models in self.model_cache.values():
                all_models.extend(models)
            return all_models
        
        # Refresh model cache
        self.model_cache = {}
        all_models = []
        
        for name, provider in self.providers.items():
            if self.health_status.get(name, False):
                try:
                    models = await provider.get_models()
                    self.model_cache[name] = models
                    all_models.extend(models)
                except Exception as e:
                    logger.error("Failed to get models from provider", provider=name, error=str(e))
        
        return all_models
    
    async def _update_health_status(self) -> None:
        """Update health status for all providers."""
        self.last_health_check = time.time()
        
        for name, provider in self.providers.items():
            try:
                self.health_status[name] = await provider.health_check()
            except Exception as e:
                logger.error("Health check failed", provider=name, error=str(e))
                self.health_status[name] = False
        
        logger.debug("Health status updated", status=self.health_status)


# Global model manager instance
model_manager = ModelManager()
