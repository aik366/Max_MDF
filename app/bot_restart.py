import asyncio
import os
from maxapi import Router, Bot, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types.attachments.buttons import CallbackButton
from config import id_klient

router = Router()
ADMIN_ID = id_klient['bot']

# Глобальные переменные
restart_task = None
countdown_messages = {}


def get_restart_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Restart PC", payload="request_restart"))
    return builder.as_markup()


def get_confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="✅ Подтвердить", payload="confirm_restart"),
        CallbackButton(text="❌ Отмена", payload="cancel_restart")
    )
    return builder.as_markup()


async def shutdown_computer():
    await asyncio.sleep(10)
    os.system("shutdown /r /t 1")  # Для Windows
    # Для Linux:
    # os.system("sudo shutdown -r now")


async def perform_countdown(bot: Bot, chat_id: int, message_id: int):
    global countdown_messages
    for i in range(9, -1, -1):
        if message_id not in countdown_messages:
            break

        try:
            # Редактируем сообщение через bot, так как event недоступен в фоновой задаче
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Компьютер перезагрузится через {i} секунд...\n"
                     "Нажмите ❌ Отмена чтобы прервать.",
                attachments=[get_confirm_keyboard()]
            )
            await asyncio.sleep(1)
        except Exception:
            break

    if message_id in countdown_messages:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Перезагрузка компьютера!",
                attachments=[]
            )
        except Exception:
            pass
        os.system("shutdown /r /t 1")


@router.message_created(F.message.body.text == "Рестарт ПК")
async def cmd_restart(event: MessageCreated):
    if event.message.sender.user_id == ADMIN_ID:
        await event.message.answer(
            "Бот управления компьютером готов к работе.",
            attachments=[get_restart_keyboard()]
        )
    else:
        await event.message.answer("У вас нет доступа к этому боту.")


@router.message_callback(F.callback.payload == "request_restart")
async def request_restart(event: MessageCallback):
    if event.callback.user.user_id != ADMIN_ID:
        await event.answer("У вас нет доступа к этой команде.")
        return

    await event.edit(
        text="Вы уверены, что хотите перезагрузить компьютер?\n"
             "После подтверждения будет 10 секунд на отмену.",
        attachments=[get_confirm_keyboard()]
    )
    await event.answer()


@router.message_callback(F.callback.payload == "confirm_restart")
async def confirm_restart(event: MessageCallback, bot: Bot):
    global restart_task, countdown_messages
    if event.callback.user.user_id != ADMIN_ID:
        await event.answer("У вас нет доступа к этой команде.")
        return

    chat_id = event.message.sender.user_id
    message_id = event.message.message_id

    restart_task = asyncio.create_task(perform_countdown(bot, chat_id, message_id))
    countdown_messages[message_id] = True

    await event.edit(
        text="Компьютер перезагрузится через 10 секунд...",
        attachments=[get_confirm_keyboard()]
    )
    await event.answer()


@router.message_callback(F.callback.payload == "cancel_restart")
async def cancel_restart(event: MessageCallback, bot: Bot):
    global restart_task, countdown_messages
    if event.callback.user.user_id != ADMIN_ID:
        await event.answer("У вас нет доступа к этой команде.")
        return

    message_id = event.message.message_id
    if message_id in countdown_messages:
        del countdown_messages[message_id]

    if restart_task and not restart_task.cancelled():
        restart_task.cancel()
        restart_task = None

    await event.edit(
        text="Перезагрузка отменена!",
        attachments=[get_restart_keyboard()]
    )
    await event.answer()
