from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str
    iat: datetime = Field(default_factory=datetime.utcnow)
