from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import Field, SQLModel


class StatusMessage(BaseModel):
    status: bool
    message: str


class UUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()"), "unique": True},
    )


class SoftDeleteModel(SQLModel):
    is_deleted: bool = Field(
        default=False,
        nullable=False,
        index=True,
        sa_column_kwargs={"server_default": text("false")},
    )


class CreateAtModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )


class UpdatedAtModel(SQLModel):
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)"),
        },
    )


class TimestampModel(CreateAtModel, UpdatedAtModel):
    pass


class DetailResp(SQLModel):
    detail: str = "success"
