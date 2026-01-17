from aiogram import Bot, Dispatcher
import aiosqlite
import os
import asyncio
from handlers import databases, menu

admin_id = 6165611649

async def main():
    TOKEN = os.getenv('TOKEN')
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    await init_db()

    dp.include_routers(databases.router, menu.router)

if __name__ == "__main__":
    asyncio.run(main())