import logging

import psycopg
from psycopg.rows import dict_row

from inventory_svc.schemas import NewItem

logger = logging.getLogger(__name__)

async def get_all_items():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory = dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT * FROM inventory
                """
            )

            return await cur.fetchall()

async def get_by_id(id: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory = dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT * FROM inventory
                WHERE id = %s
                """,
                (id,)
            )

            return await cur.fetchone()

async def get_by_isbn(isbn: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory = dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT * FROM inventory
                WHERE isbn = %s
                """,
                (isbn,)
            )

            return await cur.fetchone()

async def add_new_item(item: NewItem):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory = dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO inventory (title, author, genre, price, stock_quantity, isbn)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (item.title, item.author, item.genre, item.price, item.stock_quantity, item.isbn)
            )

            await conn.commit()
            logger.info("Record inserted successfully")

async def remove_item(id: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory = dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM inventory
                WHERE id = %s
                RETURNING id, isbn
                """,
                (id,)
            )

            await conn.commit()

            deleted_record = await cur.fetchone()
            
            logger.info(f"Record {deleted_record.get("id")} with isbn {deleted_record.get("isbn")} deleted successfully")

async def update_stock_of_item(id: str, stock_quantity: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory = dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE inventory
                SET stock_quantity = %s
                WHERE id = %s
                """,
                (stock_quantity, id,)
            )

            await conn.commit()

            logger.info(f"Update stock quantity for item id {id} successfully")

