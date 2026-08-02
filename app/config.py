from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "HR Integration Platform"
    ENV: str = "local"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    WEBHOOK_SIGNING_SECRET: str
    
    class Config:
        env_file = ".env"


settings = Settings()