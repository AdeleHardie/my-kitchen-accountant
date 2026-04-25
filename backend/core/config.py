from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: str = ""

    INITIAL_DATABASE_URL: str
    DATABASE_URL: str
        
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()