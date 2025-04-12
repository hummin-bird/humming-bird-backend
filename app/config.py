from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Humming Bird Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # ElevenLabs API settings
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_WEBHOOK_SECRET: Optional[str] = None

    # Other API keys
    GEMINI_API_KEY: Optional[str] = None
    PORTIA_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    PORTIA_BROWSER_LOCAL_CHROME_EXEC: Optional[str] = None
    PORTIA_BROWSER_LOCAL_EXTRA_CHROMIUM_ARGS: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    OPENWEATHERMAP_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
