from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.models.refresh_token import RefreshToken, RefreshTokenCreate
from app.core.db import get_async_session


class RefreshTokenCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: RefreshTokenCreate) -> RefreshToken:
        token = RefreshToken(**data.model_dump())
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def get(self, **kwargs) -> RefreshToken:
        allowed_keys = ("id", "user_id", "token_value", "is_revoked")
        for key in kwargs:
            if key not in allowed_keys:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid key",
                )

        query_filters = [RefreshToken.is_deleted == False] + [
            getattr(RefreshToken, k) == v for k, v in kwargs.items()
        ]
        stmt = select(RefreshToken).where(*query_filters)
        results = await self.session.exec(statement=stmt)
        token = results.scalar_one_or_none()

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
            )

        return token

    async def get_valid_token(self, user_id: str) -> str | None:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at >= datetime.utcnow(),
            RefreshToken.is_deleted == False,
        )
        results = await self.session.exec(statement=stmt)
        token: RefreshToken = results.scalar_one_or_none()
        return token.token_value if token else None

    async def revoke_token(self, token_id: str | UUID) -> RefreshToken:
        token: RefreshToken = await self.get(id=token_id)
        token.is_revoked = True
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def delete(self, token_id: str | UUID) -> bool:
        token: RefreshToken = await self.get(token_id)
        token.is_deleted = True

        self.session.add(token)
        await self.session.commit()

        return True


async def get_refresh_token_crud(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> RefreshTokenCRUD:
    return RefreshTokenCRUD(session=session)
