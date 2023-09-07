import asyncio
import datetime
import logging
import os

from dotenv.main import load_dotenv

from aiogram import Bot, Dispatcher, types, F, html
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import service, common, timetable, vip_handlers, cron
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middlewares.banned import BannedUpdateMiddleware

load_dotenv('config/.env')


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(os.getenv("TOKEN"))

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        cron.send_message_cron,
        trigger='interval',
        hours=24,
        start_date=datetime.datetime(2020, 2, 20, 19, 0),
        kwargs={'bot': bot}
    )
    scheduler.add_job(
        cron.change_week_cron,
        trigger='interval',
        days=7,
        start_date=datetime.datetime(2023, 8, 28, 0, 1, 0)
    )
    scheduler.start()

    dp.update.middleware(BannedUpdateMiddleware())

    dp.include_router(vip_handlers.router)
    dp.include_router(common.router)
    dp.include_router(timetable.router)
    dp.include_router(service.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
