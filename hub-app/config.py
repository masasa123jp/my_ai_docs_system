# .\hub-app\config.py
import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    CORS_ALLOWED_ORIGINS: str = Field(default="", env="CORS_ALLOWED_ORIGINS")
    SESSION_SECRET_KEY: str = Field(..., env="SESSION_SECRET_KEY")
    HUBAPP_URL: str = Field(..., env="HUBAPP_URL")
    CLIENT_ID: str = Field(default="", env="CLIENT_ID")
    CLIENT_SECRET: str = Field(default="", env="CLIENT_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

test = "Schemas: "