from typing import Optional
from uuid import UUID

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.auth.security import get_password_hash
from app.core.models import TimestampModel, UUIDModel

prefix = "auth"


class UserBase(SQLModel):
    username: str = Field(nullable=False, unique=True, index=True)
    email: str = Field(nullable=False, unique=True, index=True)


class User(UUIDModel, TimestampModel, UserBase, table=True):
    __tablename__ = f"{prefix}_user"

    password: str = Field(nullable=False)
    is_admin: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=False, nullable=False)


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def hash_password(cls, v: str) -> str:
        return get_password_hash(v)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "secret",
            }
        }
    }


class UserRead(UserBase):
    id: UUID
    email: EmailStr
    is_admin: bool
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "12345678-1234-5678-1234-567812345678",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "is_admin": True,
                "is_active": True,
            }
        }
    }


class UserPatch(UserBase):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "secret",
                "is_active": True,
            }
        }
    }
