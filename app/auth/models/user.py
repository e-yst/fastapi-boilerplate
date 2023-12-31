from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import EmailStr, field_serializer, field_validator, model_validator
from sqlmodel import Field, SQLModel

from app.auth.security import get_password_hash
from app.core.models import DetailResp, TimestampModel, UUIDModel

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
    email: EmailStr

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
    user_id: Optional[UUID] = Field(None, alias="id")
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    @model_validator(mode="after")
    def check_if_at_least_one(self):
        if not (self.username or self.email or self.is_active or self.is_admin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "At least one of username, email, "
                    "is_active, is_admin must be provided"
                ),
            )
        return self

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


class UserDetailResp(DetailResp):
    user: UserRead
