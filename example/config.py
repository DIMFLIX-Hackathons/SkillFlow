from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    DEEPSEEK_TOKEN: SecretStr
    HOME_PATH: Path = Path.cwd()

    model_config = SettingsConfigDict(
        env_file = f"{HOME_PATH}/.env"
    )


settings = Settings()
