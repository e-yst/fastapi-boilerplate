from typing import Literal

import pytest
from httpx import AsyncClient

from app.auth.jwt import create_token_set
from app.auth.models.user import User

endpoint = "/api/v1/auth/users/me"
user_keys = Literal["testuser", "admin"]


@pytest.mark.asyncio
async def test_get_user_account_authenticated(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    token = create_token_set(users.get("testuser").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    response = await async_client.get(endpoint, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_account_unauthenticated(async_client: AsyncClient):
    # Test unauthenticated access attempt
    # Try to access the /users/me endpoint without authentication
    response = await async_client.get(endpoint)
    assert response.status_code == 401
