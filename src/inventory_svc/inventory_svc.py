import logging

from . import inventory_json_server_repo as inv_repo

from . import exceptions

logger = logging.getLogger(__name__)

async def get_all_items():
    return await inv_repo.get_all_items()

async def get_items_low_in_stock(stock_qty):
    logger.info("Fetching low-stock items")

    res = await get_all_items()

    if res is None: return None

    low_stock_items = [ item for item in res if item.get("stock_quantity") <= 5 ]

    return {"low_stock_items": low_stock_items}

async def get_by_id(id: str):
    logger.info(f"Fetching item `{id}`")
    return await inv_repo.get_by_id(id)

async def get_by_isbn(isbn: str):
    return await inv_repo.get_by_isbn(isbn)

async def add_new_item(item):
    logger.info(f"Checking to see if ISBN {item.isbn} already exists")
    does_isbn_exist = await get_by_isbn(item.isbn)

    if does_isbn_exist is None:
        logger.info(f"Adding new item {item.id} to inventory")
        post_res = await inv_repo.post_new_item(item)

        return post_res

    logger.info(f"New item's ISBN `{item.isbn}` already exists")
    return

async def remove_item(id):
    res = await get_by_id(id)

    if res is None:
        logger.info(f"{id} does not exist. Nothing to delete")
        raise exceptions.ItemByIdNotFound(
            status_code = 404,
            item_id = id,
            detail = "Item can not be deleted"
        )

    return await remove_item(id)

async def receive_stock_of_item(id: str, inc_stock_quantity: int):
    if inc_stock_quantity < 1:
        logger.info("Stock quantity must be a number greater than one.")
        return {"error": "QUANTITY_LESS_THAN_ONE"}

    item_obj = await get_by_id(id)

    if item_obj is None:
        logger.info("Item {id} does not exist")
        return {"msg": "this item doesnt exist"}

    cur_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = cur_stock_qty + inc_stock_quantity

    logger.info(f"{id} current stock quantity: {cur_stock_qty}. Quantity received {inc_stock_quantity}")

    stock_qty = {"stock_quantity": new_stock_qty}

    return await inv_repo.inc_stock_of_item(id, stock_qty)

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

    item_count_res = await inv_repo.dec_stock_of_item(id, stock_qty_payload)

    if item_count_res.status_code == 200:
        return {'msg': f"{id} quatity updated from {cur_stock_qty} to {new_stock_qty}"}
