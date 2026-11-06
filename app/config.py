from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Order Management API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://orders:orders@localhost:5432/orders"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
