import logging

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from . import inventory_svc
from inventory_svc.schemas import NewItem

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CorrelationIdMiddleware,
    header_name = 'X-Correlation-ID',
)

# get inventory

@app.get("/items")
async def get_items():
    logger.info("Request received to fetch all items")
    return await inventory_svc.get_items()

@app.get("/items/low-stock")
async def low_inventory(stock_qty: int = 5):
    logger.info("Request received to fetch low-stock items")
    return await inventory_svc.get_items_low_in_stock(stock_qty)

@app.get("/items/{id}")
async def get_item(id):
    logger.info(f"Request received to fetch item `{id}`")
    return await inventory_svc.get_by_id(id)


# modify inv

@app.post('/items')
async def add_new_item(item: NewItem):
    logger.info(f"Request received to add new item received. Book ID: `{item}`")
    res = await inventory_svc.add_new_item(item)

    if res is None:
        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "ITEM_EXIST",
                "msg": f"item {item.isbn} already exists"
            }
        )

    return res

@app.delete("/items/{id}")
async def remove_item(id: str):
    logger.info(f"Request received to remove item received: `{id}`")

    return await inventory_svc.remove_an_item(id)


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

