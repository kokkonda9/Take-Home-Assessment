from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "gateway-service"
    database_url: str = "sqlite:///./gateway.db"
    account_service_url: str = "http://127.0.0.1:8081"
    host: str = "0.0.0.0"
    port: int = 8080
    http_timeout_seconds: float = 2.0
    retry_attempts: int = 3


settings = Settings()
