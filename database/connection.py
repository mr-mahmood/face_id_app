import asyncpg
import os

from app.config import DB_URL

pool = None
async def connect_db():
    global pool
    pool = await asyncpg.create_pool(dsn=DB_URL)

async def get_pool():
    global pool
    if pool is None:
        await connect_db()
    return pool