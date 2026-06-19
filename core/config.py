from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()