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

    openrouter_api_key: str = ""
    model: str = "deepseek/deepseek-chat-v3-0324:free"

    log_level: str = "INFO"


settings = Settings()
