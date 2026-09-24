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
    # does this item exist
    does_isbn_exist = await get_by_isbn(item.isbn)
    print(does_isbn_exist)

    if not does_isbn_exist:
        post_res = await post_new_item(item)
        return post_res
    else:
        return {"err": f"item {item.isbn} already exists"}

async def remove_an_item(id):
    print(f"id {id}")
    res = await get_by_id(id)
    print(res)

    if res is None:
        logger.info("nothing to delete")
        return {'msg': 'nothing to delete'}

    await remove_item(id)

async def receive_stock_of_item(id: str, inc_stock_quantity: int):
    item_obj = await get_by_id(id)

    if item_obj is None:
        return {"msg": "this item doesnt exist"}

    old_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = old_stock_qty + inc_stock_quantity

    stock_qty = {"stock_quantity": new_stock_qty}

    return await inc_stock_of_item(id, stock_qty)

async def sold_stock_of_item(id: str, sold_stock_quantity: int):
     #get current stock of item
    item_obj = await get_by_id(id)
    if item_obj is None:
        return {'msg': f"{id} does not exists"}

    old_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = old_stock_qty - sold_stock_quantity

    if new_stock_qty < 0:
        return {"msg": f"we dont have that many stock. cur stock is {old_stock_qty}. tried to sell {stock_quantity}"}

    stock_qty = {"stock_quantity": new_stock_qty}

    item_count_res = await dec_stock_of_item(id, stock_qty)
    if item_count_res.status_code == 200:
        return {'msg': f"qty updated from {old_stock_qty} to {new_stock_qty} for {id}"}
