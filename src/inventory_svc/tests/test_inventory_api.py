import pytest

from fastapi.testclient import TestClient

from inventory_svc import exceptions
from inventory_svc.inventory_api import app

client = TestClient(app)

def test_get_all_items(mocker):
    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.get_all_items",
        return_value = [
            {'id': 'BK-1001'}
        ]
    )

    res = client.get("/items")

    assert res.status_code == 200
    assert res.json()[0]["id"] == "BK-1001"

def test_get_low_inventory(mocker):
    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.get_items_low_in_stock",
        return_value = {"low_stock_items": [{}, {}]}
    )
    res = client.get("/items/low-stock")

    assert res.status_code == 200
    assert len(res.json()["low_stock_items"]) == 2

def test_get_item_by_id_success(mocker):
    id = "BK-1001"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.get_by_id",
        return_value = {"id": "BK-1001"}
    )
    res = client.get(f"/items/{id}")

    assert res.status_code == 200
    assert res.json()["id"] == id

def test_get_item_by_id_failure(mocker):
    id = "BK-1001"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.get_by_id",
        return_value = None
    )

    res = client.get(f"/items/{id}")

    assert res.status_code == 404
    assert res.json()["error"] == "ITEM_BY_ID_NOT_FOUND"
    assert res.json()["msg"] == "Item BK-1001 not found. "

def test_post_item_success(mocker):
    payload = {
        "title": "test",
        "author": "person",
        "genre": "buddhism",
        "price": "5.99",
        "stock_quantity": "20",
        "isbn": "978-05se425559474"
    }

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.add_new_item",
        return_value = {"isbn": "978-05se425559474"}
    )

    res = client.post("/items", json = payload)

    assert res.status_code == 200
    assert res.json()["isbn"] == "978-05se425559474"

def test_post_item_isbn_already_exist_failure(mocker):
    payload = {
        "title": "test",
        "author": "person",
        "genre": "buddhism",
        "price": "5.99",
        "stock_quantity": "20",
        "isbn": "978-05se425559474"
    }

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.add_new_item",
        side_effect = exceptions.ItemExists(id="978-05se425559474", detail="")
    )

    res = client.post("/items", json = payload)

    assert res.status_code == 409
    assert res.json()["error"] == "ITEM_EXISTS"

def test_remove_item_success(mocker):
    id = "BK-0000"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.remove_item",
        return_value = {"msg": f"{id} deleted"}
    )

    res = client.delete(f"/items/{id}")

    assert res.status_code == 200
    assert res.json()["msg"] == f"{id} deleted"

def test_remove_item_not_found(mocker):
    id = "BK-0000"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.remove_item",
        side_effect = exceptions.ItemByIdNotFound(item_id = id, detail = "")
    )

    client.delete(f"/items/{id}")

def test_receive_stock_of_item_invalid_quantity(mocker):
    id = "BK-0000"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.receive_stock_of_item",
        side_effect = exceptions.QuantityInvalid(item_id = id, detail = "")
    )

    res = client.post(f"/items/{id}/receive?stock_quantity=1")

    assert res.status_code == 422

def test_receive_stock_of_item_item_doesnt_exists(mocker):
    id = "BK-0000"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.receive_stock_of_item",
        side_effect = exceptions.ItemByIdNotFound(item_id = id, detail = "")
    )

    res = client.post(f"/items/{id}/receive?stock_quantity=1")

    assert res.status_code == 404
    assert res.json()["error"] == "ITEM_BY_ID_NOT_FOUND"

def test_receive_stock_of_item_success(mocker):
    id = "BK-1001"
    cur_stock_qty = 5
    rec_stock_qty = 3

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.receive_stock_of_item",
        return_value = {"stock_quantity": 8}
    )

    res = client.post(f"/items/{id}/receive?stock_quantity={rec_stock_qty}")

    assert res.status_code == 200
    assert res.json()["stock_quantity"] == cur_stock_qty + rec_stock_qty

def test_sell_stock_of_item_invalid_quantity(mocker):
    id = "BK-0000"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.sold_stock_of_item",
        side_effect = exceptions.QuantityInvalid(item_id = id, detail = "")
    )

    res = client.post(f"/items/{id}/sell?stock_quantity=1")

    assert res.status_code == 422

def test_sell_stock_of_item_item_doesnt_exists(mocker):
    id = "BK-0000"

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.sold_stock_of_item",
        side_effect = exceptions.ItemByIdNotFound(item_id = id, detail = "")
    )

    res = client.post(f"/items/{id}/sell?stock_quantity=1")

    assert res.status_code == 404
    assert res.json()["error"] == "ITEM_BY_ID_NOT_FOUND"

def test_sell_stock_of_item_success(mocker):
    id = "BK-1001"
    cur_stock_qty = 5
    sell_stock_qty = 3

    mocker.patch(
        "inventory_svc.inventory_api.inventory_svc.sold_stock_of_item",
        return_value = {"stock_quantity": 2}
    )

    res = client.post(f"/items/{id}/sell?stock_quantity={sell_stock_qty}")

    assert res.status_code == 200
    assert res.json()["stock_quantity"] == cur_stock_qty - sell_stock_qty

