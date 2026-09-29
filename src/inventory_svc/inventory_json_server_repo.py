# TODO MOVE ALL HTTPEXCEPTIONS TO API LAYER

import logging

import httpx

from .exceptions import JsonServerRepoError

logger = logging.getLogger(__name__)

url =  "http://localhost:3000"

async def get_by_isbn(isbn: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items?isbn={isbn}")

        # if able to retrieve and the obj is empty `[]`
        if res.status_code == 200 and not res.json():
            logger.info(f"ISBN {isbn} not found")

            return None
        return res.json()

async def get_by_id(id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{url}/items/{id}")

        if res.status_code == 404:
            logger.info(f"Item {id} not found")
            return None

        return res.json()

async def get_all_items():
    logger.debug("Fetching all items")

    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://localhost:3000/items/")

        if res.status_code == 200 and not res.json():
            logger.info("No items found")
            return res

        # needs testing
        if res.status_code == 404:
            logger.error(f"Not found, {res.url}")
            return None

        return res.json()

# this needs testing
async def post_new_item(item):
    async with httpx.AsyncClient() as client:
        payload = item.model_dump()

        res = await client.post(
            url = "http://localhost:3000/items",
            json = payload
        )

        logger.info("New item was stored")

        return res


async def remove_item(id):
    logger.debug(f"Removing item `{id}")

    async with httpx.AsyncClient() as client:
        res = await client.delete(f"{url}/items/{id}")

        if(res.status_code == 404):
            return None

        logger.info(f"{id} deleted")

        return {'msg': f"{id} deleted"}

async def dec_stock_of_item(id: str, payload: int):
    logger.debug(f"Decreasing item {id} stock")

    url_builder = f"{url}/items/{id}/"

    try:
        async with httpx.AsyncClient() as client:
            res = await client.patch(
                url = url_builder,
                json = payload
            )

            logger.info(f"{id} quantity decreased to {payload.get("stock_quantity")}")

            return res
    except httpx.HTTPError as err:
        raise JsonServerRepoError(f"Dont know what happened, {err}")

async def inc_stock_of_item(id: str, payload: dict):
    logger.debug(f"Increasing item {id} stock")

    url_builder = f"{url}/items/{id}/"

    try:
        async with httpx.AsyncClient() as client:
            res = await client.patch(
                url = url_builder,
                json = payload
            )

            logger.info(f"{id} quantity increased to {payload.get("stock_quantity")}")

            return res.json()
    except httpx.HTTPError as err:
        raise JsonServerRepoError(f"Dont know what happened, {err}")
