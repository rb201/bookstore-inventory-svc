import logging

from asgi_correlation_id import correlation_id

from . import inventory_repo as inv_repo
from . import exceptions
from inventory_svc.schemas import NewItem

logger = logging.getLogger(__name__)

async def get_all_items():
    return await inv_repo.get_all_items()

async def get_items_low_in_stock(stock_quantity: int):
    if stock_quantity < 0:
        logger.info(
            f"Quantity provided {stock_quantity} is invalid",
            extra = {
                "event": "invalid_quantity",
                "correlation_id": correlation_id.get(),
            }
        )
        raise exceptions.InvalidQuantityThreshold()

    logger.info("Fetching low-stock items")

    res = await get_all_items()

    low_stock_items = [ item for item in res if item.get("stock_quantity") <= stock_quantity ]

    return {"low_stock_items": low_stock_items}

async def get_by_id(id: str):
    logger.info(f"Fetching item `{id}`")
    return await inv_repo.get_by_id(id)

async def get_by_isbn(isbn: str):
    return await inv_repo.get_by_isbn(isbn)

#reformat add_new_item()
async def add_new_item(item: NewItem):
    logger.info(f"Checking to see if ISBN {item.isbn} already exists")
    does_isbn_exist = await get_by_isbn(item.isbn)

    if does_isbn_exist is not None:
        logger.info(
            f"New item's ISBN `{item.isbn}` already exists.",
            extra = {
                "event": "item_exists_error",
                "correlation_id": correlation_id.get(),
                "isbn": item.isbn,
            }
        )
        raise exceptions.ItemExists(
            id = item.isbn,
            detail = {
                "error": "ITEM_EXISTS",
                "detail": f"Can not add item with isbn {item.isbn} to inventory"
            }
        )

    logger.info(f"Adding new item {item.isbn} to inventory")
    post_res = await inv_repo.add_new_item(item)

    return post_res

async def remove_item(id):
    res = await get_by_id(id)

    if res is None:
        logger.info(f"Item id {id} does not exist. Nothing to delete")
        raise exceptions.ItemByIdNotFound(
            item_id = id,
            detail = "Item can not be deleted"
        )

    return await inv_repo.remove_item(id)

async def receive_stock_of_item(id: str, inc_stock_quantity: int):
    if inc_stock_quantity < 1:
        logger.info("Stock quantity must be a number greater than zero.")
        raise exceptions.QuantityInvalid(
            item_id = id,
            detail = {
                "error": "INVALID_QUANTITY",
                "detail": "Stock quantity must be a number greater than one."
            }
        )

    item = await get_by_id(id)

    if item is None:
        logger.info("Item {id} does not exist")
        raise exceptions.ItemByIdNotFound(
            item_id = id,
            detail = {
                "error": "ITEM_BY_ID_DOES_NOT_EXISTS",
                "detail": "Can not increase inventory"
            }
        )

    cur_stock_qty = item.get('stock_quantity')
    new_stock_qty = cur_stock_qty + inc_stock_quantity

    logger.info(f"Item id {id} current stock quantity: {cur_stock_qty}. Quantity received {inc_stock_quantity}")

    return await inv_repo.update_stock_of_item(id, new_stock_qty)

async def reduce_stock_of_item(id: str, stock_to_sell: int):
    item = await get_by_id(id)

    if item is None:
        logger.info(
            f"Item {id} does not exist",
            extra = {
                "event": "item_does_not_exist",
                "correlation_id": correlation_id.get(),
                "id": id,
            }
        )
        raise exceptions.ItemByIdNotFound(
            item_id = id,
            detail = "Can not sell inventory"
        )

    cur_stock_qty = item.get('stock_quantity')
    new_stock_qty = cur_stock_qty - stock_to_sell

    logger.info(f"{id} current stock quantity: {cur_stock_qty}. Quantity to sell {stock_to_sell}")

    if stock_to_sell > cur_stock_qty:
        logger.error("Stock quantity must be greater than available.")
        raise exceptions.QuantityInvalid(
            item_id = id,
            detail = {
                "error": "INSUFFICIENT_STOCK",
                "msg": f"Stock quantity must be greater than available, which is {cur_stock_qty}"
            }
        )

    return await inv_repo.update_stock_of_item(id, new_stock_qty)

async def process_reserve_request(request):
    reservation_id = request.reservation_id
    items = request.items

    item_not_in_inv, item_not_enough_inv = await check_inventory_and_stock(items)

    if item_not_in_inv or item_not_enough_inv:
        return await validate_inventory_check(item_not_in_inv, item_not_enough_inv)

    for item in items:
        reservation_exists = await check_reservation_exists(reservation_id, item)
        if reservation_exists:
            continue

        await reduce_stock_of_item(item.book_id, item.quantity)
        await inv_repo.create_reservation(reservation_id, item)

    return {'msg': 'ok'}

async def check_inventory_and_stock(items):
    logger.info(
        "Checking inventory availability",
        extra = {
            "event": "inventory_availability_request",
            "correlation_id": correlation_id.get(),
        }
    )
    item_not_in_inv = []
    item_not_enough_inv = []

    for item in items:
        logger.info(f"OrderItem: Item {item.title}: qty {item.quantity}")
        res = await inv_repo.get_by_id(item.book_id)

        if res is None:
            logger.info(
                f"Item {item.book_id} not found in inv",
                extra = {
                    "event": "item_not_found_in_inventory",
                    "correlation_id": correlation_id.get(),
                    "book_id": item.book_id
                }
            )
            item_not_in_inv.append(item.book_id)
            continue

        item_inv_qty = res.get('stock_quantity')
        logger.info(f"Item {item.book_id} current stock {item_inv_qty}")

        if item_inv_qty < item.quantity:
            logger.info(
                f"Item {item.book_id} does not have enough inv",
                extra = {
                    "event": "inventory_availability_request",
                    "correlation_id": correlation_id.get(),
                    "book_id": item.book_id,
                    "current_inventory": item_inv_qty,
                    "requested_inventory": item.quantity
                })
            item_not_enough_inv.append(item.book_id)

    return item_not_in_inv, item_not_enough_inv

async def validate_inventory_check(item_not_in_inv, item_not_enough_inv):
    order_errors = []

    if item_not_in_inv:
        logger.info(
            f"Order can not be completed. These items do not exist {item_not_in_inv}",
            extra = {
                "event": "create_order_failed",
                "correlation_id": correlation_id.get(),
                "items": item_not_in_inv
            }
        )

        items_not_found_error_msg = {
            "error": "ITEMS_NOT_FOUND",
            "msg": f"These items were not found {item_not_in_inv}"
        }

        order_errors.append(items_not_found_error_msg)

    if item_not_enough_inv:
        logger.info(
            f"Order can not be completed. Insufficient inv for items {item_not_enough_inv}",
            extra = {
                "event": "create_order_failed",
                "correlation_id": correlation_id.get(),
                "items": item_not_enough_inv,
            }
        )

        items_not_enough_inv_msg = {
            "error": "INSUFFICIENT_INV",
            "msg": f"These items don't have enough inv {item_not_enough_inv}"
        }
        order_errors.append(items_not_enough_inv_msg)

    if order_errors:
        order_error_msg = {
            "error": "ORDER_UNPROCESSABLE",
            "msg": "Unable to process this order. See details below",
        }
        order_error_msg["details"] = order_errors

    logger.info(order_error_msg)
    return order_error_msg

async def check_reservation_exists(reservation_id, item):
    logger.info(f"/Checking if reservation already exist for item {item.book_id}")
    reserve_exists = await inv_repo.check_reservation_exists(reservation_id, item)

    if reserve_exists:
        logger.info(f"Reservation exists for item {item.book_id}")
        return True
    return False