from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_name: str = "StartupIQ"
    project_version: str = "1.0.0"
    project_description: str = "An AI-powered Startup Idea Validation Platform"

    google_api_key: str = ""
    model: str = "gemini-2.5-flash"

    llm_temperature: float = 0.2
    llm_max_tokens: int = 4096
    llm_timeout: int = 60
    llm_retry_max_attempts: int = 3
    llm_retry_delay: float = 1.0
    llm_retry_backoff: float = 2.0

    log_level: str = "INFO"


settings = Settings()
