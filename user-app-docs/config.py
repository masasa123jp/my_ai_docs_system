# ._bk\user-app-docs\config.py

import os
from pydantic import BaseSettings, Field

class DocsSettings(BaseSettings):
    DOCAPP_DB_URL: str = os.getenv("DATABASE_URL")
    HUBAPP_URL: str = Field(..., env="HUBAPP_URL")
    CLIENT_ID: str = Field(..., env="CLIENT_ID")
    CLIENT_SECRET: str = Field(..., env="CLIENT_SECRET")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    OAUTH2_AUTHORIZE_URL: str = Field("/authorize", env="OAUTH2_AUTHORIZE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
