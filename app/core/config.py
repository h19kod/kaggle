from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Kaggle-like Data Science Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "sqlite:///./kaggle_platform.db"
    # For PostgreSQL: "postgresql://user:password@localhost:5432/kaggle_platform"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Object Storage (MinIO or AWS S3)
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "kaggle-platform"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False

    # Docker
    DOCKER_REGISTRY: str = "docker.io"
    DATA_SCIENCE_IMAGE: str = "jupyter/datascience-notebook:latest"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
