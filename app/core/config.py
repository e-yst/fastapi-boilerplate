from pydantic import PostgresDsn, field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

from app.core.constants import Environment


class Config(BaseSettings):
    DB_CONN_STR: PostgresDsn

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

    @field_validator("DB_CONN_STR")
    def sync_to_async_str(cls, v: MultiHostUrl) -> MultiHostUrl:
        async_conn_scheme = "postgresql+asyncpg"
        if v.scheme == async_conn_scheme:
            return v
        return v.build(
            scheme=async_conn_scheme,
            hosts=v.hosts(),
            path=v.path.lstrip("/"),
        )


settings = Config()
