import logging

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from . import inventory_svc, exceptions
from inventory_svc.schemas import NewItem

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CorrelationIdMiddleware,
    header_name = 'X-Correlation-ID',
)

exceptions.register_exception_handlers(app)

@app.get("/items")
async def get_all_items():
    logger.info("Request received to fetch all items")
    res = await inventory_svc.get_all_items()

    if not res:
        raise HTTPException(
            status_code = 404,
            detail = {
                "info": "ITEMS_NOT_FOUND",
                "msg": "There were no items returned"
            }
        )

    if res is None:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": "URL_NOT_FOUND?",
                "msg": f"URL {res.url} is not avail"
            }
        )

    return res

@app.get("/items/low-stock")
async def low_inventory(stock_qty: int = 5):
    logger.info("Request received to fetch low-stock items")
    res = await inventory_svc.get_items_low_in_stock(stock_qty)

    if res is None:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": "URL_NOT_FOUND?",
                "msg": f"URL {res.url} is not avail"
            }
        )

    return res

@app.get("/items/{id}")
async def get_item(id):
    logger.info(f"Request received to fetch item `{id}`")
    res = await inventory_svc.get_by_id(id)

    if res is None:
        raise exceptions.ItemByIdNotFound(
            item_id = id,
            detail = ""
        )
    return res
# modify inv

@app.post('/items')
async def add_new_item(item: NewItem):
    logger.info(f"Request received to add new item received. Book ID: `{item}`")
    return await inventory_svc.add_new_item(item)

@app.delete("/items/{id}")
async def remove_item(id: str):
    logger.info(f"Request received to remove item: `{id}`")
    return await inventory_svc.remove_item(id)


#inv sold/receive

@app.post("/items/{id}/receive")
async def item_stock_receive(id: str, stock_quantity: int):
    logger.info(f"Request received to increase item {id} stock by {stock_quantity}")
    return await inventory_svc.receive_stock_of_item(id, stock_quantity)

@app.post("/items/{id}/sell")
async def item_stock_sell(id: str, stock_quantity: int):
    logger.info(f"Request received to deccrease item {id} stock by {stock_quantity}")
    return await inventory_svc.sold_stock_of_item(id, stock_quantity)

@app.post("/items/{id}/adjust_stock")
async def adjust_stock_count(id: str, stock_quantity: int):
    logger.info(f"Request received to adjust item {id} stock")
    pass

