import logging
import json
import httpx
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url =  "http://localhost:3000"

async def fetch_by_isbn(isbn: str):
    async with httpx.AsyncClient() as client:
        res =  await client.get(f"http://localhost:3000/items?isbn={isbn}")
    
        return res.json()

async def fetch_by_id(id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{url}/items/{id}")

        if res.status_code == 404:
            return None

        if (res.status_code == 200):
            return res.json()

async def fetch_all_items():
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

async def remove_item(id):
    #check if exist
    # print(f"id {id}")
    # res = await get_by_id(id)

    # if res is None:
    #     logger.info("nothing to delete")
    #     return {'msg': 'nothing to delete'}
    
    async with httpx.AsyncClient() as client:
        res = await client.delete(f"{url}/items/{id}")

        print(res.status_code)
        if(res.status_code == 404):
            return {'msg': 'unable to deltete'}
        return {'msg': f"{id} deleted"}

async def dec_stock_of_item(id: str, payload: int):
    url_builder = f"{url}/items/{id}/"

    async with httpx.AsyncClient() as client:
        res = await client.patch(
            url = url_builder,
            json = payload
        )

        print(res.json())
        return res

async def inc_stock_of_item(id: str, payload: dict):
    url_builder = f"{url}/items/{id}/"
    async with httpx.AsyncClient() as client:
        res = await client.patch(
            url = url_builder,
            json = payload
        )

        return res.json()

# async def get_items_low_in_stock(stock_qty):
#     res = await get_all_items()

#     low_stock_items = [ item for item in res if item.get("stock_quantity") <= 5 ]

#     return {"low_stock_items": low_stock_items}
