import pytest
from httpx import AsyncClient

endpoint = "/api/v1/auth/users"


@pytest.mark.asyncio
async def test_valid_user_registration(async_client: AsyncClient):
    # Test valid user registration
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword",
    }
    response = await async_client.post(endpoint, json=user_data)

    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_duplicate_username_registration(async_client: AsyncClient):
    # Test registration with duplicate username
    user_data = {
        "username": "testuser",  # Use an existing username
        "email": "another_test@example.com",
        "password": "differentpassword",
    }
    await async_client.post(endpoint, json=user_data)
    response = await async_client.post(endpoint, json=user_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_email_registration(async_client: AsyncClient):
    # Test registration with invalid email format
    user_data = {
        "username": "newuser",
        "email": "invalidemail",  # Invalid email format
        "password": "password123",
    }
    response = await async_client.post(endpoint, json=user_data)
    assert response.status_code == 422
