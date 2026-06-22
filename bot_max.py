import asyncio
from maxapi import Bot, Dispatcher, F
from maxapi.enums import ParseMode
from maxapi.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from config import MAX_TOKEN, id_klient

# Импорт роутеров из приложения
from app import (
    handlers,
    handlers_bimgor,
    handlers_admin,
    handlers_nc_stanok,
    handlers_it_stanok,
    archive,
    bot_restart
)
from app.handlers_notes import router_notes

# Импорт функций для планировщика
from fas import send_msg_cron, shutdown, update_func, taskkill, zamen_smol, zamen_big

# Инициализация бота и диспетчера
bot = Bot(token=MAX_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# async def set_commands():
#     """Установка команд меню бота"""
#     commands = [
#         BotCommand(command='start', description='Старт'),
#         BotCommand(command='info', description='Информация'),
#         BotCommand(command='admin', description='Администратор'),
#     ]
#     await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


# async def start_bot():
#     """Действия при запуске бота"""
#     await set_commands()
#     await bot.send_message(chat_id=id_klient['bot'], text='Я запущен🥳.')
#
#
# async def stop_bot():
#     """Действия при остановке бота"""
#     await bot.send_message(chat_id=id_klient['bot'], text='Бот остановлен. За что?😔')


async def main():
    # Подключение всех роутеров к диспетчеру
    dp.include_routers(
        handlers_admin.router,
        handlers.router,
        handlers_nc_stanok.router,
        handlers_it_stanok.router,
        archive.router,
        bot_restart.router,
        router_notes,
        handlers_bimgor.router
    )

    # Регистрация хуков запуска и остановки
    # dp.startup.register(start_bot)
    # dp.shutdown.register(stop_bot)

    # Настройка планировщика задач (APScheduler)
    # scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # Примечание: если функции в fas.py отправляют сообщения, им может понадобиться
    # экземпляр bot вместо dp. Если возникнут ошибки, замените args=(dp,) на args=(bot,)
    # scheduler.add_job(
    #     send_msg_cron, 'cron', day_of_week='mon-fri', hour=17, minute=0,
    #     start_date=datetime.now(), args=(dp,)
    # )
    #
    # # scheduler.add_job(
    # #     shutdown, 'cron', day_of_week='mon-sun', hour=5, minute=30,
    # #     start_date=datetime.now(), args=(dp,)
    # # )
    #
    # scheduler.add_job(
    #     update_func, 'interval', minutes=15, args=(dp,)
    # )
    #
    # scheduler.add_job(
    #     taskkill, 'interval', minutes=30, args=(dp,)
    # )

    # scheduler.add_job(
    #     zamen_smol, 'cron', day_of_week='mon-fri', hour=16, minute=50,
    #     start_date=datetime.now(), args=(dp,)
    # )
    # scheduler.add_job(
    #     zamen_big, 'cron', day_of_week='mon-fri', hour=17, minute=10,
    #     start_date=datetime.now(), args=(dp,)
    # )

    # scheduler.start()

    # Очистка вебхука и запуск polling
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        print('Бот запущен!!!')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')