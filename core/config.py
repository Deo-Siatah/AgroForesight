from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    AUTH_SECRET: str = "dev-auth-secret"
    AUTH_TOKEN_TTL_MINUTES: int = 60 * 24

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()