from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "BTC-SHIELD Backend"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    
    DATABASE_URL: str = "sqlite:///btcshield.db"
    
    JWT_SECRET: str = "dev-insecure-secret-key-32-chars-long-min"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://pramendra0001.github.io"
    ]
    
    AI_PROVIDER: str = "mock"
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 50
    INGESTION_BATCH_SIZE: int = 1000

    @model_validator(mode="after")
    def validate_security(self):
        if self.ENVIRONMENT.lower() == "production":
            insecure_defaults = [
                "supersecretkey-change-in-production",
                "dev-insecure-secret-key-32-chars-long-min",
                "secret",
                "changeme",
                "changeme123"
            ]
            if not self.JWT_SECRET or self.JWT_SECRET in insecure_defaults or len(self.JWT_SECRET) < 32:
                raise ValueError("In production mode, JWT_SECRET must be explicitly set and be at least 32 characters long.")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("In production mode, CORS_ORIGINS must not contain '*' when allow_credentials=True.")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
