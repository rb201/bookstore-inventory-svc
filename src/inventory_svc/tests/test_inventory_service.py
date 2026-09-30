from inventory_svc import inventory_svc, exceptions

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

@pytest.mark.asyncio
async def test_get_item_by_isbn_success(mocker):
    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_by_id",
        return_value = {
            "isbn": "978-0399590504"
        }
    )

    result = await inventory_svc.get_by_id("978-0399590504")

    assert result["isbn"] == "978-0399590504"
    assert len(result) == 1

@pytest.mark.asyncio
async def test_remove_item_that_does_not_exist(mocker):
    mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.get_by_id",
        return_value = None
    )

    with pytest.raises(exceptions.ItemByIdNotFound, match = "ITEM_BY_ID_DOES_NOT_EXISTS"):
        result = await inventory_svc.remove_item("BK-1004zzz")

@pytest.mark.asyncio
async def test_remove_item_success(mocker):
    item = "BK-1004"

    mock_get_item_by_id = mocker.patch(
        "inventory_svc.inventory_svc.get_by_id",
        return_value = {
            "id": "BK-1004"
        }
    )

    mock_remote_item = mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.remove_item",
        return_value = {'msg': f"{item} deleted"}
    )

    result = await inventory_svc.remove_item(item)

    assert result["msg"] == f"{item} deleted"

@pytest.mark.asyncio
async def test_add_new_item_isbn_already_exists(mocker):
    """Test failure of adding new time because isbn already exists"""

    mock_item_obj = mocker.Mock(isbn="1234567890")

    mocker.patch(
        "inventory_svc.inventory_svc.get_by_isbn",
        return_value = {
            "isbn": "1234567890"
        }
    )

    with pytest.raises(exceptions.ItemExists):
        result = await inventory_svc.add_new_item(mock_item_obj)

@pytest.mark.asyncio
async def test_add_new_item_success(mocker):
    """Test succces of adding new item"""
    mock_item_obj = mocker.Mock(isbn=1234567890)

    mock_isbn_doesnt_exist = mocker.patch(
        "inventory_svc.inventory_svc.get_by_isbn",
        return_value = None
    )

    mock_post_new_item = mocker.patch(
        "inventory_svc.inventory_svc.inv_repo.post_new_item",
        return_value = {
            "id": "VjuvLTIJp78"
        }
    )

    result = await inventory_svc.add_new_item(mock_item_obj)

    assert result["id"] == "VjuvLTIJp78"
