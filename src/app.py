from aiogram.utils import executor
from bot import dp
import asyncpg
import os

DB_CONFIG = {
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

async def conn_db():
    return await asyncpg.connect(**DB_CONFIG)

if __name__ == '__main__':
    from handlers import register_handlers
    register_handlers()
    
    executor.start_polling(dp, skip_updates=True)