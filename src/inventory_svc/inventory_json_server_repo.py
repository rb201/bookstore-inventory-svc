import logging
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

url =  "http://localhost:3000"

async def fetch_by_isbn(isbn: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items?isbn={isbn}")

        if res.status_code == 404:
            logger.info(f"ISBN {isbn} not found")

            raise HTTPException(
                status_code = 404,
                detail = f"ISBN {isbn} not found"
            )
    
        return res.json()

async def fetch_by_id(id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{url}/items/{id}")

        if res.status_code == 404:
            logger.info(f"Item {id} not found")

            raise HTTPException(
                status_code = 404,
                detail = f"Item {id} not found"
            )

        if (res.status_code == 200):
            logger.debug(f"Item {id} found")

            return res.json()

async def fetch_all_items():
    logger.debug("Fetching all items")

    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items/")

        if res.status_code == 404:
            raise HTTPException(
                status_code = 404,
                detail = "Items not found",
            )

        return res.json()

# TODO
# cleanup function and exception handling
async def post_new_item(item):
    async with httpx.AsyncClient() as client:
        try:
            payload = item.model_dump()

            res = await client.post(
                url = "http://localhost:3000/items",
                json = payload
            )
            logger.info(res.status_code)
            logger.info("New item was stored")
            return {'item': 'created'}

        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
        
        return

async def remove_item(id):
    logger.debug(f"Removing item `{id}")

    async with httpx.AsyncClient() as client:
        res = await client.delete(f"{url}/items/{id}")

        if(res.status_code == 404):
            return {'msg': 'unable to deltete'}

        logger.info(f"{id} deleted")

        return {'msg': f"{id} deleted"}

async def dec_stock_of_item(id: str, payload: int):
    logger.debug(f"Decreasing item {id} stock")

    url_builder = f"{url}/items/{id}/"

    async with httpx.AsyncClient() as client:
        res = await client.patch(
            url = url_builder,
            json = payload
        )

        logger.error(f"{id} quantity decreased to {payload.get("stock_quantity")}")

        return res

async def inc_stock_of_item(id: str, payload: dict):
    logger.debug(f"Increasing item {id} stock")

    url_builder = f"{url}/items/{id}/"

    async with httpx.AsyncClient() as client:
        res = await client.patch(
            url = url_builder,
            json = payload
        )

        logger.error(f"{id} quantity increased to {payload.get("stock_quantity")}")

        return res.json()
