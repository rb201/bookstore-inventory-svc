from inventory_svc import inventory_svc

import pytest

@pytest.mark.asyncio
async def test_get_all_items_success(mocker):

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

