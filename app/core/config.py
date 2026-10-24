from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RADAR_", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/radar"
    default_locale: str = "ru"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Admin dashboard (/admin on radar-women). Sign-in with Google, then the
    # email must be on admin_emails. Empty client id or secret = admin disabled.
    google_client_id: str = ""
    admin_emails: list[str] = []
    admin_session_secret: str = ""
    admin_session_days: int = 7
    # False only for local http development
    admin_cookie_secure: bool = True


settings = Settings()
