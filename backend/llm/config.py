from pydantic import BaseModel, Field

from backend.utils.config import settings


class LLMConfig(BaseModel):
    model: str = Field(
        default="deepseek/deepseek-chat-v3-0324:free",
        description="Model identifier passed to the provider",
    )
    temperature: float = Field(default=0.7, ge=0, le=2, description="Generation temperature")
    max_tokens: int = Field(default=4096, gt=0, description="Maximum tokens per generation")
    timeout: float = Field(default=60.0, gt=0, description="Request timeout in seconds")
    api_key: str = Field(default="", description="API key for the LLM provider")
    base_url: str | None = Field(default=None, description="Optional base URL for the provider")

    retry_max_attempts: int = Field(
        default=3, ge=0, description="Maximum retry attempts on failure"
    )
    retry_delay: float = Field(default=1.0, ge=0, description="Initial retry delay in seconds")
    retry_backoff: float = Field(default=2.0, ge=1.0, description="Retry delay multiplier")

    @classmethod
    def from_settings(cls) -> "LLMConfig":
        return cls(
            model=settings.model,
            api_key=settings.openrouter_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            timeout=settings.llm_timeout,
            retry_max_attempts=settings.llm_retry_max_attempts,
            retry_delay=settings.llm_retry_delay,
            retry_backoff=settings.llm_retry_backoff,
        )

    @classmethod
    def from_env(cls) -> "LLMConfig":
        import os

        return cls(
            model=os.getenv("MODEL", "deepseek/deepseek-chat-v3-0324:free"),
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
            timeout=float(os.getenv("LLM_TIMEOUT", "60.0")),
            retry_max_attempts=int(os.getenv("LLM_RETRY_MAX_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("LLM_RETRY_DELAY", "1.0")),
            retry_backoff=float(os.getenv("LLM_RETRY_BACKOFF", "2.0")),
            base_url=os.getenv("LLM_BASE_URL", None),
        )

    def to_provider_kwargs(self) -> dict:
        return {
            "id": self.model,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }
