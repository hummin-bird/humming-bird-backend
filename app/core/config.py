from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Humming Bird Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # ElevenLabs API settings
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_WEBHOOK_SECRET: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
