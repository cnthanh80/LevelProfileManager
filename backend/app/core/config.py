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

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
