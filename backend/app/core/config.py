from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    frontend_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    llm_provider: str = "groq"
    llm_model: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_secret_key: str = ""
    data_repository: str = "supabase"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key)

    @property
    def supabase_data_api_url(self) -> str:
        url = self.supabase_url.rstrip("/")
        return url if url.endswith("/rest/v1") else f"{url}/rest/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
