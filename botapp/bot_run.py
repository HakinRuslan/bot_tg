import asyncio
import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from bot import bot, dp
from conf import *
from db.middleware.middleware import *
from user.user_router import *
from user.cat_router import *
from admin.router import *

async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

# Функция, которая выполнится, когда бот запустится
async def start_bot():
    await set_commands()
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")

# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in ADMINS:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")


async def main():
    print("запустилось приложуха")
    # scheduler.add_job(send_time_msg, 'interval', seconds=10)
    # scheduler.start()

    dp.update.middleware(DBMiddlewareWithComm())
    dp.update.middleware(DBMiddlewareWithoutComm())
    dp.include_router(catalog_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    # dp.startup.register(start_bot)
    # dp.shutdown.register(stop_bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())