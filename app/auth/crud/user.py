from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.models.user import User, UserCreate, UserPatch
from app.core.db import get_async_session


class UsersCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> User:
        """
        Create a new user in the database.

        Args:
            data (UserCreate): The data required to create a new user. It includes the username, email, and password.

        Returns:
            User: The newly created user object.
        """
        await self.check_user_unique_fields(data)

        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get(self, **kwargs) -> User:
        """
        Retrieve a user from the database based on the provided parameters.

        Args:
            **kwargs: A dictionary of keyword arguments that can include the user's ID, username, or email.

        Returns:
            User: The user object retrieved from the database based on the provided parameters. If no user is found, an HTTPException is raised.
        """
        allowed_keys = ("id", "username", "email")
        for key in kwargs:
            if key not in allowed_keys:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid key",
                )
        stmt = select(User).where(
            *(getattr(User, key) == kwargs[key] for key in kwargs)
        )
        results = await self.session.execute(statement=stmt)
        user = results.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    async def update(self, user_id: str | UUID, user_patch: UserPatch) -> User:
        """
        Update a user in the database based on the provided user ID.

        Args:
            user_id (str or UUID): The ID of the user to be updated.
            user (UserPatch): The user to be updated.

        Returns:
            User: The updated user.

        """
        user = await self.get(id=user_id)
        update_data = user_patch.model_dump(exclude_none=True, exclude_unset=True)
        for k, v in update_data.items():
            setattr(user, k, v)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete(self, user_id: str | UUID) -> bool:
        """
        Delete a user from the database based on the provided user ID.

        Args:
            user_id (str or UUID): The ID of the user to be deleted.

        Returns:
            bool: True if the user was successfully deleted from the database.
        """
        stmt = delete(User).where(User.id == user_id)

        await self.session.execute(statement=stmt)
        await self.session.commit()

        return True

    async def check_user_unique_fields(self, user: UserCreate):
        """
        Check if a user with the same username or email already exists in the database.

        Args:
            user (UserCreate): The data of the user to be checked for uniqueness. It includes the username and email.

        Raises:
            HTTPException: If a user with the same username or email already exists.
        """
        stmt = select(User.id).where(
            or_(User.email == user.email, User.username == user.username)
        )
        result = await self.session.execute(statement=stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists",
            )


async def get_users_crud(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UsersCRUD:
    return UsersCRUD(session=session)


UsersCrudDep = Annotated[UsersCRUD, Depends(get_users_crud)]
