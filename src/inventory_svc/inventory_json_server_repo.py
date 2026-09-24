import logging
import json
import httpx
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url =  "http://localhost:3000"

async def get_by_isbn(isbn: str):
    async with httpx.AsyncClient() as client:
        res =  await client.get(f"http://localhost:3000/items?isbn={isbn}")
    
        return res.json()

async def get_by_id(id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{url}/items/{id}")

        if res.status_code == 404:
            return None

        if (res.status_code == 200):
            return res.json()

async def get_all_items():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items/")

        return res.json()

async def post_new_item(item):
    async with httpx.AsyncClient() as client:
        try:
            payload = item.model_dump()
            # print(payload)

            res = await client.post(
                url = "http://localhost:3000/items",
                json = payload
            )
            logger.info(res.status_code)
            return {'item': 'created'}

        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        
        return

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
    #check if exist
    print(f"id {id}")
    res = await get_by_id(id)

    if res is None:
        logger.info("nothing to delete")
        return {'msg': 'nothing to delete'}
    
    async with httpx.AsyncClient() as client:
        res = await client.delete(f"{url}/items/{id}")

        print(res.status_code)
        if(res.status_code == 404):
            return {'msg': 'unable to deltete'}
        return {'msg': f"{id} deleted"}

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

    async with httpx.AsyncClient() as client:
        url_builder = f"{url}/items/{id}/"
        res = await client.patch(
            url = url_builder,
            json = stock_qty
        )

        print(res)
        return {
            f'msg': f"qty updated from {old_stock_qty} to {new_stock_qty} for {id}"
        }

async def receive_stock_of_item(id: str, inc_stock_quantity: int):
    item_obj = await get_by_id(id)

    if item_obj is None:
        return {"msg": "this item doesnt exist"}

    old_stock_qty = item_obj.get('stock_quantity')
    new_stock_qty = old_stock_qty + inc_stock_quantity

    stock_qty = {"stock_quantity": new_stock_qty}

    url_builder = f"{url}/items/{id}/"
    async with httpx.AsyncClient() as client:
        res = await client.patch(
            url = url_builder,
            json = stock_qty
        )

        return {
            f'msg': f"qty updated from {old_stock_qty} to {new_stock_qty} for {id}"
        }

async def get_items_low_in_stock(stock_qty):
    res = await get_all_items()

    low_stock_items = [ item for item in res if item.get("stock_quantity") <= 5 ]

    return {"low_stock_items": low_stock_items}
