import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.db import get_async_session
from app.main import app


@pytest.fixture(scope="session")
def db_engine():
    engine = create_async_engine(
        settings.DB_CONN_STR.unicode_string(),
        echo=True,
        future=True,
    )
    yield engine


@pytest_asyncio.fixture(scope="function")
async def db(db_engine: AsyncSession):
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db):
    app.dependency_overrides[get_async_session] = lambda: db
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as c:
        yield c
