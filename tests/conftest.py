import asyncio
from typing import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlmodel import SQLModel, select

from app.auth.models.user import User
from app.auth.security import get_password_hash
from app.core.config import settings

engine = create_async_engine(
    settings.DB_CONN_STR.unicode_string(),
    echo=settings.is_debug,
    future=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        async with async_session(bind=conn) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture()
def app(override_get_db: Callable) -> FastAPI:
    from app.core.db import get_async_session
    from app.main import app

    app.dependency_overrides[get_async_session] = override_get_db

    return app


@pytest_asyncio.fixture()
async def async_client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        yield ac


@pytest_asyncio.fixture()
async def users(db_session: AsyncSession) -> dict[str, User]:
    user_data = {
        "admin": {
            "username": "admin",
            "password": get_password_hash("adminpass"),
            "email": "admin@example.com",
            "is_active": True,
            "is_admin": True,
        },
        "testuser": {
            "username": "testuser",
            "password": get_password_hash("userpass"),
            "email": "testuser@example.com",
        },
        "testuser2": {
            "username": "testuser2",
            "password": get_password_hash("userpass"),
            "email": "testuser2@example.com",
        },
    }

    stmt = select(User).where(User.username.in_(user_data.keys()))
    result = await db_session.execute(stmt)
    users: list[User] = result.scalars().all()
    if users:
        return {u.username: u for u in users}

    users = [User(**user_data[i]) for i in user_data]
    db_session.add_all(users)
    await db_session.commit()
    return {u.username: u for u in users}
