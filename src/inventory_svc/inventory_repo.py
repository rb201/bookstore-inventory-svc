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
    
        logger.info(res.json())
        logger.info(res.status_code)
    return res.json()

async def get_by_id(id: str):
    print('in get-by_id()')
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{url}/items/{id}")

        # print(res)
        if res.status_code == 404:
            return None
            print(res.status_code)

        if (res.status_code == 200):
            print(f"id {id} found")
            print(res.json())
            return res.json()

def update_book_stock(id: str, quantity: int):
    pass

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
        return res
    else:
        return {"err": f"item {item.isbn} already exists"}

async def inc_item_count(id, info):
    #does it exists
    does_item_exist = await get_by_id(id)
    print(does_item_exist)

    if not does_item_exist:
        return {'msg': f"{id} does not exist"}
    
    print("what i have", info.stock_quantity)
    old_stock = info.stock_quantity
    # get fields i need
    cur_stock_quantity = does_item_exist.get("stock_quantity")
    print(cur_stock_quantity)
    cur_stock_quantity += old_stock

    # async with httpx.AsyncClient() as client:
    #     payload = {"stock_quantity": stock_quantity}
    #     res = await client.patch(
    #         url = f"{url}/items/{id}",
    #         json = json.load(payload))

    #     print(res.status_code)
    #     if(res.status_code == 200):
    #         return {'msg': f"{id} was updated"}

    #     return {'msg': 'some problem arose'}

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

