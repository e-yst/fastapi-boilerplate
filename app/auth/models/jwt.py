from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: UUID
    typ: Literal["access", "refresh"]
    iat: datetime = Field(default_factory=datetime.utcnow)
    exp: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=15)
    )

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.exp.replace(tzinfo=None)

    @property
    def time_to_expire(self) -> timedelta:
        return self.exp.replace(tzinfo=None) - datetime.utcnow()

    @field_serializer("sub")
    def serialize_sub(self, sub: UUID):
        return str(sub)


class RefreshTokenReq(BaseModel):
    refresh_token: str
