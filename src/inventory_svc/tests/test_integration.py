import pytest
import pytest_asyncio
from httpx2 import AsyncClient, ASGITransport

from inventory_svc import inventory_api, inventory_svc, exceptions, schemas
from inventory_svc.inventory_api import app

@pytest_asyncio.fixture(scope="module")
async def client():
    """A single, shared async client for all tests within the same module."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_get_item_success(client):
    res = await client.get("/items/1")

    assert res.status_code == 200
    assert res.json()["title"] == "test"

@pytest.mark.asyncio
async def test_get_item_not_found(client):
    book_id = "666"

    # with pytest.raises(exceptions.ItemByIdNotFound, match = f"Item {book_id} not found."):
    res = await client.get(f"/items/{book_id}")

    assert res.status_code == 404
    assert res.json()["error"] == "ITEM_BY_ID_NOT_FOUND"

# @pytest.mark.asyncio
# async def test_create_item_success(mocker):
#     new_item = mocker.Mock(
#         spec = schemas.NewItem,
#         title = "Integration tests for meditators"
#         author = "test01"
#         genre = "fiction"
#         price = .99
#         stock_quantity = 201
#         isbn = "987-1234567890"
#     )

#     added_item = await inventory_api.add_new_item(item)

# @pytest.mark.asyncio
# async def test_remove_item_success("4"):
#     removed_item = await inventory_api.remove_item(item)

# @pytest.mark.asyncio
# async def test_

# @pytest.mark.asyncio
# async def test_

# @pytest.mark.asyncio
# async def test_