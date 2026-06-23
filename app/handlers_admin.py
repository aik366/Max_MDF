import os
import json
import sqlite3
from datetime import datetime
from collections import defaultdict
from maxapi import Router, Bot, F
from maxapi.types import MessageCreated, Command, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.attachments.attachment import ButtonsPayload
from maxapi.types.input_media import InputMedia
from app import keyboards as kb
from app import database as db
from config import id_klient
from fas import *
from app.smart_lab import *
from pochta.gmail_app import *

router = Router()


class Reg(StatesGroup):
    text_1 = State()
    text_2 = State()
    img = State()
    delete_account = State()
    add_surname = State()
    add_account = State()


class Change(StatesGroup):
    change_zakaz = State()
    number_zakaz = State()


class Actions(StatesGroup):
    new_action = State()
    change_action = State()
    edit_action = State()
    add_action = State()
    del_action = State()
    view_action = State()


class PhotoForm(StatesGroup):
    waiting_for_photo = State()
    waiting_for_caption = State()


class AddState(StatesGroup):
    waiting_for_amount = State()


class EditState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_date = State()


# ================= НАСТРОЙКИ =================
DB_NAME = "DATA/finance.db"

MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}


# =============================================
# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================
def format_date_for_user(db_date: str) -> str:
    y, m, d = db_date.split("-")
    return f"{d}.{m}.{y}"


async def show_edit_list(target, is_callback=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, date FROM records ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    builder = InlineKeyboardBuilder()
    if rows:
        for row in rows:
            r_id, amount, date = row
            amount_str = f"{amount:g}"
            user_date = format_date_for_user(date)
            builder.row(CallbackButton(text=f"{amount_str} ₽ | {user_date}", payload=f"edit_rec:{r_id}"))

    builder.row(CallbackButton(text="« В главное меню", payload="back_to_start"))

    text = "Выберите запись для редактирования:" if rows else "📭 Нет записей для редактирования."

    if is_callback:
        await target.edit(text=text, attachments=[builder.as_markup()])
    else:
        await target.answer(text, attachments=[builder.as_markup()])


# ================= ОБРАБОТЧИКИ =================

@router.message_created(Command("admin"))
async def cmd_admin(event: MessageCreated):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        await event.message.answer("Привет Администратор", attachments=[kb.kb_admin])


@router.message_created(F.message.body.text == "Объявление")
async def cmd_admin_ad(event: MessageCreated, context: MemoryContext):
    await context.set_state(Reg.text_1)
    await event.message.answer("Пишите объявление")


@router.message_created(Reg.text_1, F.message.body.text != '✖ Отмена')
async def reg_admin_text_1(event: MessageCreated, context: MemoryContext):
    bot = event.bot  # Получаем бота из события
    await context.update_data(msg=event.message.body.text)
    full_data = await context.get_data()
    await context.clear()

    if await db.db_check(event.message.sender.user_id, "Admin"):
        for id, name, surname in await db.db_select():
            try:
                await bot.send_message(chat_id=int(id), text=f"Привет {name}\n{full_data['msg']}\nАдминистрация!!!")
            except Exception as e:
                await bot.send_message(chat_id=id_klient['bot'],
                                       text=f'Ошибка при отправке сообщения пользователю {id}: {e}')


@router.message_created(F.message.body.text == "Аккаунты")
async def cmd_admin_ak(event: MessageCreated):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        info = ''
        for id, name, surname in await db.db_select():
            info += f"{id}: {name}, {surname}\n"
        await event.message.answer(info)


@router.message_created(F.message.body.text == "Картинка")
async def start_photo_upload(event: MessageCreated, context: MemoryContext):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        await event.message.answer("📷 Отправьте фото, к которому нужно добавить подпись")
        await context.set_state(PhotoForm.waiting_for_photo)


@router.message_created(PhotoForm.waiting_for_photo, F.message.photo)
async def process_photo(event: MessageCreated, context: MemoryContext):
    photo = event.message.photo[-1]
    await context.update_data(photo_id=photo.file_id)
    await context.set_state(PhotoForm.waiting_for_caption)
    await event.message.answer("✅ Фото принято! Теперь введите подпись к фото")


@router.message_created(PhotoForm.waiting_for_caption, F.message.body.text)
async def process_caption(event: MessageCreated, context: MemoryContext):
    bot = event.bot  # Получаем бота из события
    await context.update_data(caption=event.message.body.text)
    full_data = await context.get_data()
    await context.clear()

    for tg_id, name, data in await db.db_select():
        try:
            img = InputMedia(file_id=full_data['photo_id'])
            attachment = await bot.upload_media(img)
            await bot.send_message(chat_id=int(tg_id), text=f"Привет {name}!\n{full_data['caption']}\nАдминистрация!!!",
                                   attachments=[attachment])
        except Exception as e:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f'Ошибка при отправке сообщения пользователю {tg_id}: {e}')


@router.message_created(F.message.body.text == "Удалить")
async def cmd_admin_del(event: MessageCreated, context: MemoryContext):
    await context.set_state(Reg.delete_account)
    await event.message.answer("Пишите ID аккаунта")


@router.message_created(Reg.delete_account, F.message.body.text != '✖ Отмена')
async def reg_admin_del_account(event: MessageCreated, context: MemoryContext):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        await db.db_delete(event.message.body.text)
        # Отвечаем в тот же чат, откуда пришло сообщение
        await event.message.answer("Аккаунт удален")
        await context.clear()


@router.message_created(F.message.body.text == "Добавить")
async def cmd_admin_add(event: MessageCreated, context: MemoryContext):
    await context.set_state(Reg.add_account)
    await event.message.answer("Пишите ID аккаунта\nИ через пробел фамилию")


@router.message_created(Reg.add_account, F.message.body.text != '✖ Отмена')
async def reg_admin_add_account(event: MessageCreated, context: MemoryContext):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        id_name, name = event.message.body.text.split(" ", 1)
        await db.cmd_start_db(id_name, name)
        # Отвечаем в тот же чат, откуда пришло сообщение
        await event.message.answer("Аккаунт добавлен")
        await context.clear()


@router.message_created(F.message.body.text == "Обновить")
async def cmd_admin_update(event: MessageCreated, context: MemoryContext):
    await context.set_state(Reg.add_surname)
    await event.message.answer("Пишите ID аккаунта\nИ через пробел фамилию")


@router.message_created(Reg.add_surname, F.message.body.text != '✖ Отмена')
async def reg_admin_del_surname(event: MessageCreated, context: MemoryContext):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        id_name, surname = event.message.body.text.split(" ", 1)
        await db.db_update(id_name, surname)
        # Отвечаем в тот же чат, откуда пришло сообщение
        await event.message.answer("Аккаунт обновлен")
        await context.clear()


@router.message_created(F.message.body.text == "✖ Отмена")
async def cmd_admin_cancel(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Действие отменено")


@router.message_created(F.message.body.text == "🔙 Назад")
async def cmd_admin_back(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Это Бимгор бот", attachments=[kb.kb_bot])


@router.message_created(F.message.body.text == "Переписать")
async def cmd_admin_rewrite(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Замена заказа", attachments=[kb.in_change_order])


@router.message_created(F.message.body.text == "🔄 Рестарт")
async def cmd_restart_bot(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Рестарт через 3 сек")
    os.startfile("bot_run.vbs")


@router.message_callback(F.callback.payload == "zakaz_value")
async def zakaz_value(event: MessageCallback):
    if order_number():
        bt = [[CallbackButton(text=f"{i}", payload=f"bt_{i}") for i in order_number()]]
        payload = ButtonsPayload(buttons=bt).pack()
        await event.message.answer(f"Заказ №", attachments=[payload])
    else:
        await event.message.answer(f"Заказов нет!!!")
    await event.answer()


@router.message_callback(F.callback.payload.startswith("bt_"))
async def bt_open(event: MessageCallback, context: MemoryContext):
    await context.set_state(Change.number_zakaz)
    call_data = event.callback.payload.split("_")[1]
    await context.update_data(num_zakaz=call_data)

    bt_open = [[
        CallbackButton(text="Small", payload="small_value"),
        CallbackButton(text="Big", payload="big_value"),
        CallbackButton(text="Delete", payload="delete_value")
    ]]
    payload = ButtonsPayload(buttons=bt_open).pack()

    await event.message.answer(f'Заказ № {call_data}', attachments=[payload])
    await event.answer()


@router.message_callback(Change.number_zakaz)
async def smol_value(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()
    if event.callback.payload == "small_value":
        await event.message.answer("Маленький обновлено!", zamena(1, data['num_zakaz']))
    elif event.callback.payload == "big_value":
        await event.message.answer("Большой обновлено!", zamena(0, data['num_zakaz']))
    elif event.callback.payload == "delete_value":
        await event.message.answer("Заказ удален!", delete_number(data['num_zakaz']))
    await event.answer()
    await context.clear()


# @router.message_callback(F.callback.payload == "open_value")
# async def open_value(event: MessageCallback):
#     await event.message.answer("Открыта!!!", change_open())
#     await event.answer()
#
#
# @router.message_callback(F.callback.payload == "close_value")
# async def close_value(event: MessageCallback):
#     await event.message.answer("Закрыта!!!", change_close())
#     await event.answer()


@router.message_callback(F.callback.payload == "change_value")
async def change_value(event: MessageCallback, context: MemoryContext):
    await context.set_state(Change.change_zakaz)
    await event.message.answer(f"Заказов в базе {' '.join(order_number())}\nПишите номер заказа после ???")
    await event.answer()


@router.message_created(Change.change_zakaz)
async def ms_change_value(event: MessageCreated, context: MemoryContext):
    text = event.message.body.text
    if text.startswith("???"):
        number = text[3:]
        await event.message.answer(f"Заказ {number} обновлено!!!", change_namber(number))
    else:
        await event.message.answer("пишите ??? после номер заказа")
    await context.clear()


@router.message_created(F.message.body.text == "Акции")
async def cmd_actions_bot(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Выберите действия!!!", attachments=[kb.in_actions])


@router.message_callback(F.callback.payload == "view_actions")
async def view_actions(event: MessageCallback):
    await event.message.answer(f"{await viev_ticers()}")
    await event.answer()


def load_portfolio(filepath: str = "DATA/ticker_json.json") -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@router.message_callback(F.callback.payload == "view_add_actions")
async def add_actions(event: MessageCallback, context: MemoryContext):
    portfolio = load_portfolio()
    builder = InlineKeyboardBuilder()
    for ticker, data in portfolio.items():
        if ticker == "IMOEX":
            continue
        builder.button(CallbackButton(text=f"{ticker} {data[0]}", payload=f"ticker_{ticker}_{data[0]}"))
    builder.button(CallbackButton(text="Добавить", payload="add_actions"))
    builder.adjust(1)

    await event.message.answer(f"Выберите акцию", attachments=[builder.as_markup()])
    await event.answer()


@router.message_callback(F.callback.payload.startswith("ticker_"))
async def ticker_open(event: MessageCallback, context: MemoryContext):
    ticker_name, ticker_number = event.callback.payload.upper().split("_")[1:]
    await context.update_data(ticker_name=ticker_name, ticker_number=ticker_number)

    builder = InlineKeyboardBuilder()
    builder.button(CallbackButton(text="Новое значение", payload="new_actions"))
    builder.button(CallbackButton(text="Добавить акции", payload="change_actions"))
    builder.button(CallbackButton(text="Удалить", payload="del_actions"))
    builder.button(CallbackButton(text="Выход", payload="exit_actions"))
    builder.adjust(1)

    await event.message.answer(f"Выберите действие", attachments=[builder.as_markup()])
    await event.answer()


@router.message_callback(F.callback.payload == "new_actions")
async def new_actions(event: MessageCallback, context: MemoryContext):
    await context.set_state(Actions.new_action)
    await event.message.answer("Новое значение акции")
    await event.answer()


@router.message_created(Actions.new_action)
async def ms_new_action(event: MessageCreated, context: MemoryContext):
    name_number = int(event.message.body.text)
    data = await context.get_data()
    await event.message.answer(f"Акция {data['ticker_name']} обновлено!!!",
                               update_json_file(data['ticker_name'], name_number),
                               attachments=[kb.in_actions])
    await context.clear()


@router.message_callback(F.callback.payload == "change_actions")
async def change_actions(event: MessageCallback, context: MemoryContext):
    await context.set_state(Actions.change_action)
    await event.message.answer("Количество акций\nКоторую хотите добавить")
    await event.answer()


@router.message_created(Actions.change_action)
async def ms_change_action(event: MessageCreated, context: MemoryContext):
    number = int(event.message.body.text)
    data = await context.get_data()
    number += int(data['ticker_number'])
    await event.message.answer(f"Акция {data['ticker_name']} обновлено!!!",
                               update_json_file(data['ticker_name'], number),
                               attachments=[kb.in_actions])
    await context.clear()


@router.message_callback(F.callback.payload == "del_actions")
async def del_actions(event: MessageCallback, context: MemoryContext):
    del_keyboard = InlineKeyboardBuilder()
    del_keyboard.button(CallbackButton(text="Удалить", payload="delete_actions"))
    del_keyboard.button(CallbackButton(text="Выход", payload="exit_actions"))
    del_keyboard.adjust(2)

    data = await context.get_data()
    await event.message.answer(f"Удалить акцию {data['ticker_name']}?", attachments=[del_keyboard.as_markup()])
    await event.answer()


@router.message_callback(F.callback.payload == "delete_actions")
async def delete_actions(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()
    await event.message.answer(f"Акция {data['ticker_name']} удалена!!!", delete_json_file(data['ticker_name']))
    await context.clear()
    await event.answer()


@router.message_callback(F.callback.payload == "exit_actions")
async def exit_actions(event: MessageCallback, context: MemoryContext):
    await event.message.answer("Выберите действия!!!", attachments=[kb.in_actions])
    await context.clear()
    await event.answer()


@router.message_callback(F.callback.payload == "add_actions")
async def add_actions_new(event: MessageCallback, context: MemoryContext):
    await context.set_state(Actions.add_action)
    await event.message.answer("Имя акции пробел\nколичество акций\nНапример: LKOH 100")
    await event.answer()


@router.message_created(Actions.add_action)
async def ms_add_action(event: MessageCreated, context: MemoryContext):
    name_number = event.message.body.text.upper().split(" ")
    await event.message.answer(f"Акция {name_number[0]} добавлена!!!",
                               update_json_file(name_number[0], name_number[1]),
                               attachments=[kb.in_actions])
    await context.clear()


# ================= ФИНАНСЫ =================

@router.message_callback(F.callback.payload == "view_add_finance")
async def view_finance(event: MessageCallback, context: MemoryContext):
    init_db()
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="➕ Добавить", payload="action_add"))
    builder.row(CallbackButton(text="📊 Просмотр", payload="action_view"))
    builder.row(CallbackButton(text="✏️ Редактировать", payload="action_edit"))

    await event.message.answer("👋 Добро пожаловать! Выберите действие:", attachments=[builder.as_markup()])
    await context.clear()
    await event.answer()


@router.message_callback(F.callback.payload == "back_to_start")
async def cb_back_to_start(event: MessageCallback):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="➕ Добавить", payload="action_add"))
    builder.row(CallbackButton(text="📊 Просмотр", payload="action_view"))
    builder.row(CallbackButton(text="✏️ Редактировать", payload="action_edit"))

    await event.edit(text="Выберите действие:", attachments=[builder.as_markup()])
    await event.answer()


@router.message_callback(F.callback.payload == "action_add")
async def cb_add(event: MessageCallback, context: MemoryContext):
    await context.set_state(AddState.waiting_for_amount)
    await event.edit(text="💰 Введите сумму для добавления:")
    await event.answer()


@router.message_created(AddState.waiting_for_amount)
async def msg_add_amount(event: MessageCreated, context: MemoryContext):
    try:
        amount = float(event.message.body.text.replace(',', '.'))
        db_date = datetime.now().strftime("%Y-%m-%d")
        user_date = datetime.now().strftime("%d.%m.%Y")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (amount, date) VALUES (?, ?)", (amount, db_date))
        conn.commit()
        conn.close()

        await event.message.answer(f"✅ Сохранено: <b>{amount:g} ₽</b> на {user_date}")
        await context.clear()
    except ValueError:
        await event.message.answer("❌ Пожалуйста, введите корректное число (например, 1500 или 1500.50).")


@router.message_callback(F.callback.payload == "action_view")
async def cb_view(event: MessageCallback):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT amount, date FROM records ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await event.edit(text="📭 Записей пока нет.")
        await event.answer()
        return

    months = defaultdict(list)
    grand_total = 0.0

    for amount, date in rows:
        month = date[:7]
        months[month].append((amount, date))
        grand_total += amount

    text = "📊 <b>Статистика по месяцам:</b>\n\n"

    for month, records in sorted(months.items()):
        month_total = sum(record[0] for record in records)
        year, month_num = month.split("-")
        month_name = f"{MONTHS_RU[int(month_num)]} {year}"

        text += f"📅 <b>{month_name}</b>\n"
        for amt, full_date in records:
            user_date = format_date_for_user(full_date)
            text += f"  • {amt:g} ₽ - {user_date}\n"
        text += f"  <i>Итого за месяц: {month_total:g} ₽</i>\n\n"

    text += f"💰 <b>Общая сумма: {grand_total:g} ₽</b>"

    if len(text) > 4000:
        text = text[:3900] + "\n\n⚠️ <i>Список слишком длинный и был обрезан.</i>"

    await event.edit(text=text)
    await event.answer()


@router.message_callback(F.callback.payload == "action_edit")
async def cb_edit(event: MessageCallback):
    await show_edit_list(event, is_callback=True)


@router.message_callback(F.callback.payload.startswith("edit_rec:"))
async def cb_edit_rec(event: MessageCallback):
    record_id = int(event.callback.payload.split(":")[1])
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="💰 Изменить сумму", payload=f"edit_amt:{record_id}"))
    builder.row(CallbackButton(text="📅 Изменить дату", payload=f"edit_dt:{record_id}"))
    builder.row(CallbackButton(text="🗑 Удалить запись", payload=f"del_rec:{record_id}"))
    builder.row(CallbackButton(text="« Назад к списку", payload="action_edit"))

    await event.edit(text=f"⚙️ Запись #{record_id}. Выберите действие:", attachments=[builder.as_markup()])
    await event.answer()


@router.message_callback(F.callback.payload.startswith("edit_amt:"))
async def cb_edit_amt(event: MessageCallback, context: MemoryContext):
    record_id = int(event.callback.payload.split(":")[1])
    await context.update_data(record_id=record_id)
    await context.set_state(EditState.waiting_for_amount)
    await event.edit(text="💰 Введите новую сумму:")
    await event.answer()


@router.message_created(EditState.waiting_for_amount)
async def msg_edit_amt(event: MessageCreated, context: MemoryContext):
    try:
        new_amount = float(event.message.body.text.replace(',', '.'))
        data = await context.get_data()
        record_id = data.get("record_id")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET amount = ? WHERE id = ?", (new_amount, record_id))
        conn.commit()
        conn.close()

        await event.message.answer(f"✅ Сумма успешно обновлена на <b>{new_amount:g} ₽</b>")
        await context.clear()
        await show_edit_list(event.message)
    except ValueError:
        await event.message.answer("❌ Пожалуйста, введите корректное число.")


@router.message_callback(F.callback.payload.startswith("edit_dt:"))
async def cb_edit_dt(event: MessageCallback, context: MemoryContext):
    record_id = int(event.callback.payload.split(":")[1])
    await context.update_data(record_id=record_id)
    await context.set_state(EditState.waiting_for_date)
    await event.edit(text="📅 Введите новую дату в формате ДД.ММ.ГГГГ (например, 15.01.2026):")
    await event.answer()


@router.message_created(EditState.waiting_for_date)
async def msg_edit_dt(event: MessageCreated, context: MemoryContext):
    new_date_input = event.message.body.text.strip()
    try:
        parsed_date = datetime.strptime(new_date_input, "%d.%m.%Y")
        db_date = parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        await event.message.answer("❌ Неверный формат даты. Используйте строго ДД.ММ.ГГГГ (например, 15.01.2026).")
        return

    data = await context.get_data()
    record_id = data.get("record_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET date = ? WHERE id = ?", (db_date, record_id))
    conn.commit()
    conn.close()

    await event.message.answer(f"✅ Дата успешно обновлена на <b>{new_date_input}</b>")
    await context.clear()
    await show_edit_list(event.message)


@router.message_callback(F.callback.payload.startswith("del_rec:"))
async def cb_del_rec(event: MessageCallback):
    record_id = int(event.callback.payload.split(":")[1])
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    await event.answer("✅ Запись удалена")
    await show_edit_list(event, is_callback=True)