import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from tools.database import *

import config
from handlers.main_handlers import dp as router
from handlers.check_handlers import dp as router2
from handlers.sensors_handlers import dp as router3
from handlers.notification_handlers import dp as router4


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    default = DefaultBotProperties(parse_mode= ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.include_router(router2)
    dp.include_router(router3)
    dp.include_router(router4)

    conn = create_connection(15, 3)
    create_table(conn)
    conn.close()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())