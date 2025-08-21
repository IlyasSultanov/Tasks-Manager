from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    project_name: str = Field(default="Task Manager", alias="PROJECT_NAME")
    version: str = Field(default="1.0.0", alias="VERSION")
    db_url: str = Field(alias="DATABASE_URL")
    debug: bool = Field(default=False, alias="DEBUG")


settings = Config()