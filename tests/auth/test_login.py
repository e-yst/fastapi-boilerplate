from typing import Literal

import pytest
from httpx import AsyncClient

from app.auth.models.jwt import Token
from app.auth.models.user import User

endpoint = "/api/v1/auth/token"
user_keys = Literal["testuser", "admin"]


@pytest.mark.asyncio
async def test_valid_login(async_client: AsyncClient, users: dict[user_keys, User]):
    # Test valid user login
    login_data = {
        "username": "testuser@example.com",
        "password": "userpass",
    }
    response = await async_client.post(endpoint, data=login_data)
    assert response.status_code == 200
    assert Token.model_validate(response.json())


@pytest.mark.asyncio
async def test_invalid_login(async_client: AsyncClient):
    # Test invalid user login
    login_data = {
        "username": "invalid_username@example.com",
        "password": "invalid_password",
    }
    response = await async_client.post(endpoint, data=login_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_missing_credentials(async_client: AsyncClient):
    # Test login with missing credentials
    login_data = {}  # No username or password provided
    response = await async_client.post(endpoint, data=login_data)
    assert response.status_code == 422
