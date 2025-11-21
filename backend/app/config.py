import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost/ai_hr_platform"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@aihrplatform.com")
    
    # SMS
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # External Assessment Providers
    HACKERRANK_API_KEY: str = os.getenv("HACKERRANK_API_KEY", "")
    CODESIGNAL_API_KEY: str = os.getenv("CODESIGNAL_API_KEY", "")
    TESTGORILLA_API_KEY: str = os.getenv("TESTGORILLA_API_KEY", "")
    PLURALSIGHT_API_KEY: str = os.getenv("PLURALSIGHT_API_KEY", "")
    CODILITY_API_KEY: str = os.getenv("CODILITY_API_KEY", "")
    
    # AI/ML
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Storage
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
