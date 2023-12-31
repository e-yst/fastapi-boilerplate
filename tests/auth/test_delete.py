from typing import Literal

import pytest
from httpx import AsyncClient

from app.auth.jwt import create_token_set
from app.auth.models.user import User

endpoint = "/api/v1/auth/users"
user_keys = Literal["testuser", "admin"]


@pytest.mark.asyncio
async def test_delete_user_authenticated(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test authenticated user deletion (assuming the user is an admin)
    token = create_token_set(users.get("admin").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    url = f"{endpoint}/{users.get('testuser').id}"
    response = await async_client.delete(url, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_admin_by_himself(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test authenticated admin deletion (assuming the user is an admin)
    admin_id = users.get("admin").id
    token = create_token_set(admin_id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    url = f"{endpoint}/{admin_id}"
    response = await async_client.delete(url, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_unauthorized(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test unauthorized user deletion (non-admin)
    user_id = users.get("testuser").id
    token = create_token_set(user_id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    url = f"{endpoint}/{user_id}"
    response = await async_client.delete(url, headers=headers)
    assert response.status_code == 403
