import pytest
from httpx import AsyncClient

path_prefix = "/api/v1/auth"


@pytest.mark.asyncio
async def test_regiester(client: AsyncClient):
    resp = await client.post(f"{path_prefix}/users")
    assert resp.status_code == 422
