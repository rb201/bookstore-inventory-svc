import logging

import httpx

from .inventory_json_server_repo import *

async def get_all_items():
    return await fetch_all_items()

async def get_items_low_in_stock(stock_qty):
    res = await get_all_items()

    low_stock_items = [ item for item in res if item.get("stock_quantity") <= 5 ]

    return {"low_stock_items": low_stock_items}

async def get_by_id(id: str):
    return await fetch_by_id(id)

async def get_by_isbn(isbn: str):
    return await fetch_by_isbn(isbn)

async def add_new_item(item):
    does_isbn_exist = await get_by_isbn(item.isbn)
    print(does_isbn_exist)

    if not does_isbn_exist:
        post_res = await post_new_item(item)
        return post_res
    else:
        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "ITEM_EXIST",
                "msg": f"item {item.isbn} already exists"
            }
        )

async def remove_an_item(id):
    print(f"id {id}")
    res = await get_by_id(id)
    print(res)

    if res is None:
        logger.info("nothing to delete")
        return {
            "info": "ITEM_DOES_NOT_EXIST",
            'msg': 'nothing to delete'
        }

    await remove_item(id)

async def receive_stock_of_item(id: str, inc_stock_quantity: int):
    if inc_stock_quantity < 1:
        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "INVALID_QUANTITY",
                "msg": f"Must provide a number greater than one."
            }
        )

    item_obj = await get_by_id(id)

    if item_obj is None:
        return {"msg": "this item doesnt exist"}

    old_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = old_stock_qty + inc_stock_quantity

    stock_qty = {"stock_quantity": new_stock_qty}

    return await inc_stock_of_item(id, stock_qty)

async def sold_stock_of_item(id: str, stock_to_sell: int):
    item_obj = await get_by_id(id)

    cur_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = cur_stock_qty - stock_to_sell

    if stock_to_sell > cur_stock_qty:
        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "INSUFFICIENT_STOCK",
                "msg": f"Can not sell {stock_to_sell} of {id}. Only {cur_stock_qty} available"
            }
        )

    stock_qty_payload = {"stock_quantity": new_stock_qty}

    item_count_res = await dec_stock_of_item(id, stock_qty_payload)

    if item_count_res.status_code == 200:
        return {'msg': f"{id} quatity updated from {cur_stock_qty} to {new_stock_qty}"}
