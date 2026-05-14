from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str = Field(repr=False)

    db_user: str
    db_password: str = Field(repr=False)
    db_name: str
    db_host: str
