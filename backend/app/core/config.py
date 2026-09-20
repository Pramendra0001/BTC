from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "BTC-SHIELD Backend"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///btcshield.db"
    
    JWT_SECRET: str = "dev-insecure-secret-key-32-chars-long-min"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    CORS_ORIGINS: List[str] = [
        "https://pramendra0001.github.io",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = ""
    ADMIN_EMAIL: str = "admin@btcshield.gov"
    
    AI_PROVIDER: str = "mock"
    LOG_LEVEL: str = "INFO"
    MAX_UPLOAD_SIZE_MB: int = 50
    INGESTION_BATCH_SIZE: int = 1000

    @model_validator(mode="before")
    @classmethod
    def parse_cors_origins(cls, values):
        if isinstance(values, dict):
            cors = values.get("CORS_ORIGINS")
            if isinstance(cors, str):
                import json
                cors = cors.strip()
                if cors.startswith("[") and cors.endswith("]"):
                    values["CORS_ORIGINS"] = json.loads(cors)
                else:
                    values["CORS_ORIGINS"] = [orig.strip() for orig in cors.split(",") if orig.strip()]
        return values

    @model_validator(mode="after")
    def validate_security(self):
        if self.ENVIRONMENT.lower() == "production":
            # 1. DATABASE_URL validation: Must come from environment and cannot be SQLite
            if not self.DATABASE_URL or self.DATABASE_URL.startswith("sqlite") or "btcshield.db" in self.DATABASE_URL:
                raise ValueError("In production mode, DATABASE_URL must be explicitly configured with a production database (e.g. PostgreSQL) and cannot be SQLite.")

            # 2. JWT_SECRET validation: Must be explicit, strong, and at least 32 characters
            insecure_defaults = [
                "supersecretkey-change-in-production",
                "dev-insecure-secret-key-32-chars-long-min",
                "secret",
                "changeme",
                "changeme123"
            ]
            if not self.JWT_SECRET or self.JWT_SECRET in insecure_defaults or len(self.JWT_SECRET) < 32:
                raise ValueError("In production mode, JWT_SECRET must be explicitly set and be at least 32 characters long.")

            # 3. CORS_ORIGINS validation: Disallow wildcard and ensure GitHub Pages is present
            if "*" in self.CORS_ORIGINS:
                raise ValueError("In production mode, CORS_ORIGINS must not contain '*' when allow_credentials=True.")
            if "https://pramendra0001.github.io" not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append("https://pramendra0001.github.io")

            # 4. ADMIN_PASSWORD validation if provided
            if self.ADMIN_PASSWORD:
                if self.ADMIN_PASSWORD == "admin123" or len(self.ADMIN_PASSWORD) < 12:
                    raise ValueError("In production mode, ADMIN_PASSWORD must be at least 12 characters and cannot be 'admin123'.")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
