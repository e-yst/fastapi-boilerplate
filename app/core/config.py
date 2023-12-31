from pydantic import PostgresDsn, computed_field, field_validator, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

from app.core.constants import Environment


class Config(BaseSettings):
    DB_SCHEME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    PROJECT_NAME: str = "FastAPI Template"

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None

    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_SECS: int = 5 * 60
    JWT_REFRESH_TOKEN_EXPIRE_SECS: int = 7 * 24 * 60

    @property
    def is_debug(self):
        return self.ENVIRONMENT.is_debug

    @property
    def DB_CONN_STR(self) -> PostgresDsn:
        return PostgresDsn(
            f"{self.DB_SCHEME}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Config()
