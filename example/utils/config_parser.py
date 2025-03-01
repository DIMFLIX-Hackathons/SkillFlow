from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    HOME_PATH: Path = Path.cwd()

    model_config = SettingsConfigDict(env_file=f"{HOME_PATH}/.env")
