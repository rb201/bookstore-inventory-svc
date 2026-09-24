import logging
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from .inventory_svc import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewItem(BaseModel):
    title: str
    author: str
    genre: str
    price: float
    stock_quantity: int
    isbn: str 
    # history: list[dict]

app = FastAPI()

# get inventory

@app.get("/items")
async def get_items():
    return await get_all_items()

@app.get("/items/low-stock")
async def low_inventory(stock_qty: int = 5):
    return await get_items_low_in_stock(stock_qty)

@app.get("/items/{id}")
async def get_item(id):
    return await get_by_id(id)


# modify inv

@app.post('/items')
async def add_item(item: NewItem):
    return await add_new_item(item)

@app.delete("/items/{id}")
async def remove_item(id: str):
    return await remove_an_item(id)


#inv sold/receive

@app.post("/items/{id}/receive")
async def item_stock_receive(id: str, stock_quantity: int):
    return await receive_stock_of_item(id, stock_quantity)

@app.post("/items/{id}/sell")
async def item_stock_sell(id: str, stock_quantity: int):
    return await sold_stock_of_item(id, stock_quantity)

@app.post("/items/{id}/adjust_stock")
async def adjust_stock_count(id: str, stock_quantity: int):
    pass

@app.get("/")
def get_root():
    return {"Hey": "...microservice!?"}
