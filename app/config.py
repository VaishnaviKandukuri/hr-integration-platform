from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "HR Integration Platform"
    ENV: str = "local"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REGISTERED_CLIENT_ID: str = "payroll-system-001"
    REGISTERED_CLIENT_SECRET: str = "payroll-secret-devonly-4471"
    WEBHOOK_SIGNING_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()