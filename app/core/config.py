from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RADAR_", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/radar"
    default_locale: str = "ru"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
