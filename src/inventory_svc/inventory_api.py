import logging
from typing import Optional
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from .inventory_repo import add_new_item, remove_an_item, inc_item_count


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

class UpdateItem(NewItem):
    title: Optional[str]
    author: Optional[str]
    genre: Optional[str]
    price: Optional[float]
    stock_quantity: Optional[int]
    isbn: Optional[str]

app = FastAPI()

@app.get("/items")
async def read_item():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items/")

        return {'all items': res.json()}


@app.get("/items/{id}")
async def read_item(id):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items/{id}")

        return res.json()

@app.post('/add')
async def add_item(item: NewItem):
    res = await add_new_item(item)
    return res

@app.delete("/items/{id}")
async def remove_item(id: str):
    res = await remove_an_item(id)
    return res

@app.patch("/items/{id}")
async def update_item(id, info: UpdateItem):
    res = await inc_item_count(id, info)
    return res

@app.get("/")
def get_root():
    return {"Hey": "...microservice!?"}
