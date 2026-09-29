from inventory_svc import inventory_svc

import pytest

@pytest.mark.asyncio
async def test_get_all_items_success(mocker):
    """Test a fetch that returns results"""

    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_all_items",
        return_value=[
            {
                "book_id": "BK-1001",
            }
        ]
    )

    result = await inventory_svc.get_all_items()

    assert len(result) == 1
    assert result[0]["book_id"] == "BK-1001"

@pytest.mark.asyncio
async def test_get_items_low_in_stock_none(mocker):
    """Test a fetch that returns no results for items low in stock"""

    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_all_items",
        return_value = []
    )

    result = await inventory_svc.get_items_low_in_stock(3)
    assert result["low_stock_items"] == []

@pytest.mark.asyncio
async def test_get_items_low_in_stock_success(mocker):
    """Test a fetch that returns items low in stock"""

    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_all_items",
        return_value = [
            {
            "stock_quantity": 1,
            },
            {
            "stock_quantity": 4,
            }
        ]
    )

    result = await inventory_svc.get_items_low_in_stock(5)

    assert len(result["low_stock_items"]) == 2
    assert result["low_stock_items"][0]["stock_quantity"] <= 5

@pytest.mark.asyncio
async def test_get_item_by_id_failure(mocker):
    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_by_id",
        return_value = {
            "error": "ITEM_BY_ID_NOT_FOUND",
        }
    )

    result = await inventory_svc.get_by_id("BK-11004")

    assert result["error"] == "ITEM_BY_ID_NOT_FOUND"
    assert len(result) == 1

@pytest.mark.asyncio
async def test_get_item_by_id_success(mocker):
    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_by_id",
        return_value = {
            "id": "BK-1004"
        }
    )

    result = await inventory_svc.get_by_id("BK-1004")

    assert result["id"] == "BK-1004"
    assert len(result) == 1
