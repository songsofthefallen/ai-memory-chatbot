from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    JWT_KEY: str

    CACHE_TTL: int = 800
    CONVERSATION_PER_PAGE: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()