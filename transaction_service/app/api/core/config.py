from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database ayarları
    database_url: str
    ACCOUNT_SERVICE_URL: str
    RABBITMQ_URL: str  # RabbitMQ Docker default
    # JWT ayarları
    jwt_secret: str  # her Service ile aynı olmalı!
    jwt_alg: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"  # Değerleri .env'den de okuyabilir


settings = Settings()
