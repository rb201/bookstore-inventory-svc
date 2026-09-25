import logging

from .inventory_json_server_repo import *

logger = logging.getLogger(__name__)

async def get_all_items():
    return await fetch_all_items()

async def get_items_low_in_stock(stock_qty):
    logger.info("Fetching low-stock items")

    res = await get_all_items()

    low_stock_items = [ item for item in res if item.get("stock_quantity") <= 5 ]

    return {"low_stock_items": low_stock_items}

async def get_by_id(id: str):
    logger.info(f"Fetching item `{id}`")
    return await fetch_by_id(id)

async def get_by_isbn(isbn: str):
    return await fetch_by_isbn(isbn)

async def add_new_item(item):
    logger.info(f"Checking to see if ISBN {item.isbn} already exists for new item")
    does_isbn_exist = await get_by_isbn(item.isbn)

    if not does_isbn_exist:
        logger.info("Added new item to inventory")
        post_res = await post_new_item(item)

        return post_res
    else:
        logger.info(f"New item's ISBN `{item.isbn}` already exists")

        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "ITEM_EXIST",
                "msg": f"item {item.isbn} already exists"
            }
        )

async def remove_an_item(id):
    res = await get_by_id(id)

    if res is None:
        logger.info(f"{id} does not exist. Nothing to delete")

        return {
            "info": "ITEM_DOES_NOT_EXIST",
            'msg': 'nothing to delete'
        }

    await remove_item(id)

async def receive_stock_of_item(id: str, inc_stock_quantity: int):
    if inc_stock_quantity < 1:
        logger.error("Stock quantity must be a number greater than one.")

        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "INVALID_QUANTITY",
                "msg": f"Must provide a number greater than one."
            }
        )

    item_obj = await get_by_id(id)

    if item_obj is None:
        logger.info("Item {id} does not exist")
        return {"msg": "this item doesnt exist"}

    cur_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = cur_stock_qty + inc_stock_quantity

    logger.info(f"{id} current stock quantity: {cur_stock_qty}. Quantity received {inc_stock_quantity}")

    stock_qty = {"stock_quantity": new_stock_qty}

    return await inc_stock_of_item(id, stock_qty)

async def sold_stock_of_item(id: str, stock_to_sell: int):
    item_obj = await get_by_id(id)

    cur_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = cur_stock_qty - stock_to_sell

    logger.info(f"{id} current stock quantity: {cur_stock_qty}. Quantity to sell {stock_to_sell}")

    if stock_to_sell > cur_stock_qty:
        logger.error("Stock quantity must be greater than available.")

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
