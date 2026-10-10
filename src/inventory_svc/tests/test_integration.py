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

@pytest_asyncio.fixture
async def test_create_item_fix(client):
    item_created = {}

    yield item_created

    if "id" in item_created:
        await client.delete(f"/items/{item_created["id"]}")

@pytest_asyncio.fixture
async def test_remove_item_fix(client):
    test_item = {
        "title": "Integrations",
        "author": "Mr A",
        "genre": "tech",
        "price": "11.99",
        "stock_quantity": "50",
        "isbn": "978-11111121131"
    }

    res = await client.post("/items", json = test_item)
    yield res.json()

@pytest.mark.asyncio
async def test_get_item_success(client):
    res = await client.get("/items/1")

    assert res.status_code == 200
    assert res.json()["title"] == "test"

@pytest.mark.asyncio
async def test_get_item_not_found(client):
    book_id = "666"

    res = await client.get(f"/items/{book_id}")

    assert res.status_code == 404
    assert res.json()["error"] == "ITEM_BY_ID_NOT_FOUND"

@pytest.mark.asyncio
async def test_create_item_success(client, test_create_item_fix):
    new_item = {
        "title": "Integration tests for meditators",
        "author": "test01",
        "genre": "fiction",
        "price": .99,
        "stock_quantity": 201,
        "isbn": "987-"
    }
    res = await client.post("/items", json = new_item)

    assert res.status_code == 201
    res_data = res.json()

    # this line gives the fixture the id for deletion
    test_create_item_fix["id"] = res_data["id"]
    assert res_data["isbn"] == new_item["isbn"]

@pytest.mark.asyncio
async def test_remove_item_success(client, test_remove_item_fix):
    book_id = test_remove_item_fix["id"]

    res = await client.delete(f"/items/{book_id}")

    res_data = res.json()
    assert res.status_code == 200
    assert res_data["id"] == test_remove_item_fix["id"]

