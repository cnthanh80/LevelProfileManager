from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Level Profile Manager"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    FILE_STORAGE_PATH: str = "/app/storage/uploads"

    # Notification engine - safe by default for local development.
    # When NOTIFICATION_DRY_RUN=true, messages are not sent to SMTP/Telegram,
    # but notification_logs records are still created as SENT for end-to-end tests.
    NOTIFICATION_DRY_RUN: bool = True

    SMTP_ENABLED: bool = False
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "no-reply@example.com"
    SMTP_FROM_NAME: str = "Level Profile Manager"
    SMTP_USE_TLS: bool = True
    SMTP_TIMEOUT_SECONDS: int = 15

    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_DEFAULT_CHAT_ID: str | None = None
    TELEGRAM_TIMEOUT_SECONDS: int = 15

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
