from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    RABBITMQ_URL: str
    TRANSACTION_SERVICE_URL: str
    # JWT (user_service ile aynı olmalı!)
    jwt_secret: str
    jwt_alg: str
    access_token_expire_minutes: int

    # Service URLs
    USER_SERVICE_URL: str

    # RabbitMQ
    rabbitmq_url: str

    class Config:
        env_file = ".env"


settings = Settings()
