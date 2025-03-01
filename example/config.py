from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os
from pathlib import Path

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    # DB_URL: SecretStr
    # HOME_PATH:Path = Path.cwd()
    # ADMIN_ID: int
    model_config = SettingsConfigDict(
        env_file = ".env"
    )


settings = Settings()