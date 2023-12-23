from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, computed_field
from sqlalchemy import text
from sqlmodel import Field

from app.core.config import settings
from app.core.models import SoftDeleteModel, UpdatedAtModel, UUIDModel
from app.core.utils import generate_alphanumeric

prefix = "auth"


class RefreshTokenBase(UUIDModel):
    user_id: UUID = Field(..., nullable=False, foreign_key="auth_user.id", index=True)
    token_value: str = Field(default_factory=generate_alphanumeric, nullable=False)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow()
        + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRE_SECS),
        nullable=False,
    )
    issued_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    is_revoked: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": text("false")},
    )


class RefreshToken(SoftDeleteModel, UpdatedAtModel, RefreshTokenBase, table=True):
    __tablename__ = f"{prefix}_refresh_token"

    @computed_field
    @property
    def is_expired(self) -> bool:
        return self.expires_at <= datetime.utcnow()


class RefreshTokenCreate(BaseModel):
    refresh_token: str


class RefreshTokenRead(RefreshTokenBase):
    pass
