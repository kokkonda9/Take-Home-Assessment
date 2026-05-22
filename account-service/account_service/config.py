from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "account-service"
    database_url: str = "sqlite:///./account.db"
    host: str = "0.0.0.0"
    port: int = 8081


settings = Settings()
