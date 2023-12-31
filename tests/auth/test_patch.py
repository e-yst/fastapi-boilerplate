from typing import Literal

import pytest
from httpx import AsyncClient

from app.auth.jwt import create_token_set
from app.auth.models.user import User

endpoint = "/api/v1/auth/users"
user_keys = Literal["testuser", "admin"]


@pytest.mark.asyncio
async def test_update_user_authenticated(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test authenticated user update (allowed updates by non-admin)
    token = create_token_set(users.get("testuser").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    update_data = {"password": "newpass"}
    response = await async_client.patch(endpoint, json=update_data, headers=headers)
    print(f"{response.json()=}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_by_admin(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test authenticated user update by admin
    token = create_token_set(users.get("admin").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    update_data = {
        "user_id": str(users.get("testuser").id),
        "password": "newpass",
        "is_active": True,
        "is_admin": True,
    }
    response = await async_client.patch(endpoint, json=update_data, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_forbidden(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test forbidden user update (non-admin trying to update forbidden fields)
    token = create_token_set(users.get("testuser").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    update_data = {
        "is_active": True,
        "is_admin": True,
    }
    response = await async_client.patch(endpoint, json=update_data, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_other_user_by_non_admin(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test forbidden user update (non-admin trying to update forbidden fields)
    token = create_token_set(users.get("testuser").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    update_data = {
        "user_id": str(users.get("testuser2").id),
        "is_active": True,
        "is_admin": True,
    }
    response = await async_client.patch(endpoint, json=update_data, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_invalid_data(
    async_client: AsyncClient, users: dict[user_keys, User]
):
    # Test updating user with invalid data (none of the required fields provided)
    token = create_token_set(users.get("testuser").id)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    update_data = {}  # No fields provided
    response = await async_client.patch(endpoint, json=update_data, headers=headers)
    assert response.status_code == 400
