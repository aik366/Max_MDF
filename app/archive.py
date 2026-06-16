from maxapi import Router, Bot, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.attachments.attachment import ButtonsPayload
from config import put_old, put_555ss, put_555nc, put_555it
from time import strftime
import shutil
import os

router = Router()

year, year_1, year_2 = strftime('%Y'), str(int(strftime('%Y')) - 1), str(int(strftime('%Y')) - 2)


def copy_archive(year, stanok, zakaz):
    for folder in os.listdir(f"{put_old}{year}/"):
        if int(zakaz[:4]) < int(folder.split('_')[-1]):
            puth = f"{put_old}{year}/{folder}/{stanok}/{zakaz}"
            if os.path.exists(puth):
                if zakaz[4:] == 'h':
                    shutil.copytree(puth, f"{put_555ss}/{zakaz}")
                elif zakaz[4:] == 'nc':
                    shutil.copytree(puth, f"{put_555nc}/{zakaz}")
                elif zakaz[4:] == 'it':
                    shutil.copytree(puth, f"{put_555it}/{zakaz}")
                return 'Копирование завершено.'
            else:
                return 'нет такого заказа.'
    return 'нет такого заказа.'


class Reg(StatesGroup):
    a_year = State()
    a_stanok = State()
    zakaz_n = State()


@router.message_created(F.message.body.text == "Архив")
async def arkhive_year(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Reg.a_year)

    buttons = [
        [CallbackButton(text=f"{year_2}", payload=f"yr_{year_2}"),
         CallbackButton(text=f"{year_1}", payload=f"yr_{year_1}"),
         CallbackButton(text=f"{year}", payload=f"yr_{year}")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите год: ", attachments=[payload])


@router.message_callback(Reg.a_year, F.callback.payload.startswith("yr_"))
async def arkhive_stanok(event: MessageCallback, context: MemoryContext):
    await context.update_data(a_year=event.callback.payload[3:])
    await context.set_state(Reg.a_stanok)

    buttons = [
        [CallbackButton(text="ss", payload="st_ss"),
         CallbackButton(text="nc", payload="st_nc"),
         CallbackButton(text="it", payload="st_it")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите станок: ", attachments=[payload])
    await event.answer()


@router.message_callback(Reg.a_stanok, F.callback.payload.startswith("st_"))
async def arkhive_order(event: MessageCallback, context: MemoryContext):
    await context.update_data(a_stanok=event.callback.payload[3:])
    await context.set_state(Reg.zakaz_n)
    data = await context.get_data()
    await event.message.answer(f"год: {data['a_year']} станок: {data['a_stanok']}\nВведите номер заказа: ")
    await event.answer()


@router.message_created(Reg.zakaz_n)
async def arkhive_all(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()
    message_text = ''

    if data["a_stanok"] == 'ss':
        message_text = event.message.body.text + 'h'
    elif data["a_stanok"] == 'nc':
        message_text = event.message.body.text + 'nc'
    elif data["a_stanok"] == 'it':
        message_text = event.message.body.text + 'it'

    await context.update_data(zakaz_n=message_text)
    data = await context.get_data()

    await event.message.answer(copy_archive(data['a_year'], data['a_stanok'], data['zakaz_n']))
    await context.clear()


if __name__ == "__main__":
    pass
