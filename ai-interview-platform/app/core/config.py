from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Interview Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "dev"
    DEBUG: bool = True
    JWT_SECRET: str = "dev_secret_change_me"
    DATABASE_URL: str = "sqlite:///./data/app.db"

    ACCESS_TOKEN_EXPIRES_SECONDS: int = 60 * 15
    REFRESH_TOKEN_EXPIRES_DAYS: int = 7

    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_ROOT: str = "./data/object_storage"
    STORAGE_SIGNED_URL_EXPIRES_SECONDS: int = 60 * 15
    STORAGE_MAX_FILE_SIZE_MB: int = 10
    STORAGE_S3_BUCKET: str = "ai-interview-assets"
    STORAGE_S3_ENDPOINT_URL: str | None = "http://127.0.0.1:9000"
    STORAGE_S3_REGION: str = "us-east-1"
    STORAGE_S3_ACCESS_KEY: str | None = "minioadmin"
    STORAGE_S3_SECRET_KEY: str | None = "minioadmin"

    PUBLIC_SITE_URL: str = "http://localhost:5173"

    GITHUB_API_URL: str = "https://api.github.com"
    GITHUB_API_TOKEN: str | None = None
    EXTERNAL_API_TIMEOUT_SECONDS: float = 5.0
    EXTERNAL_API_RETRIES: int = 2
    EXTERNAL_API_RATE_LIMIT_PER_MINUTE: int = 30
    EXTERNAL_API_CACHE_TTL_SECONDS: int = 300

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
