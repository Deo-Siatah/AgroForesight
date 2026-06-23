from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT = "dev-auth-secret"


class Settings(BaseSettings):
    DATABASE_URL: str

    AUTH_SECRET: str = _INSECURE_DEFAULT
    AUTH_TOKEN_TTL_MINUTES: int = 60 * 24

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    ENVIRONMENT: str = "development"
    DEBUG: bool = Fals
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-3.1-flash-lite"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _require_strong_secret(self) -> "Settings":
        if self.ENVIRONMENT != "development" and self.AUTH_SECRET == _INSECURE_DEFAULT:
            raise ValueError("AUTH_SECRET must be explicitly set in non-development environments.")
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _require_strong_secret(self) -> "Settings":
        if self.ENVIRONMENT != "development" and self.AUTH_SECRET == _INSECURE_DEFAULT:
            raise ValueError("AUTH_SECRET must be explicitly set in non-development environments.")
        return self



@lru_cache
def get_settings():
    return Settings()


settings = get_settings()