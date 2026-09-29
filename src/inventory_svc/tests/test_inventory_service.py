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
                "title": "Python Basics"
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
            "id": "BK-1005",
            "title": "Thinking, Fast and Slow",
            "author": "Daniel Kahneman",
            "genre": "Psychology",
            "price": 18,
            "stock_quantity": 1,
            "isbn": "978-0374533557"
            },
            {
            "id": "BK-1006",
            "title": "Project Hail Mary",
            "author": "Andy Weir",
            "genre": "Sci-Fi",
            "price": 16.99,
            "stock_quantity": 4,
            "isbn": "978-0593135204"
            }
        ]
    )

    result = await inventory_svc.get_items_low_in_stock(5)

    assert len(result["low_stock_items"]) == 2
    assert result["low_stock_items"][0]["stock_quantity"] <= 5
