from maxapi import Router, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.attachments.attachment import ButtonsPayload
from app.keyboards import kb_frezer, kb_frezer_it
from app.it_stanok import value_freza, value_tolshina

router = Router()

class Reg(StatesGroup):
    it_order = State()
    it_freza = State()
    it_visota = State()
    it_order_tolshina = State()
    it_select_tolshina = State()
    it_volue_tolshina = State()


@router.message_created(F.message.body.text == "it_станок")
async def number_order(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Это it станок", attachments=[kb_frezer_it])


@router.message_created(F.message.body.text == "↩️ Назад")
async def back_to_start(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Начало", attachments=[kb_frezer])


@router.message_created(F.message.body.text == "№ фрезы")
async def start_freza(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Reg.it_order)
    await event.message.answer("Введите номер заказа: ")


@router.message_created(F.message.body.text == "Толщина МДФ")
async def start_tolshina(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Reg.it_order_tolshina)
    await event.message.answer("Введите номер заказа: ")


@router.message_created(Reg.it_order_tolshina)
async def volue_tolshina(event: MessageCreated, context: MemoryContext):
    await context.update_data(n_order=event.message.body.text + "it")
    tolshina = [
        [
            CallbackButton(text="16 МДФ", payload="mdf_16"),
            CallbackButton(text="19 МДФ", payload="mdf_19"),
            CallbackButton(text="22 МДФ", payload="mdf_22")
        ]
    ]
    payload = ButtonsPayload(buttons=tolshina).pack()
    await event.message.answer("Выберите МДФ: ", attachments=[payload])


@router.message_callback(F.callback.payload.startswith("mdf_"))
async def mdf_tolshina(event: MessageCallback, context: MemoryContext):
    payload = event.callback.payload
    if payload in ["mdf_16", "mdf_19", "mdf_22"]:
        await context.update_data(select=payload)
        await context.set_state(Reg.it_volue_tolshina)
        await event.message.answer("Введите значение толщины: ")
    else:
        await event.message.answer("Ошибка")
        await context.clear()
    await event.answer()


@router.message_created(Reg.it_volue_tolshina)
async def itogo_tolshina(event: MessageCreated, context: MemoryContext):
    await context.update_data(n_visota=event.message.body.text)
    data = await context.get_data()
    await event.message.answer(value_tolshina(data['n_order'][:-2], int(data['select'][-2:]), data['n_visota']))
    await context.clear()


@router.message_created(Reg.it_order)
async def number_freza(event: MessageCreated, context: MemoryContext):
    await context.update_data(n_order=event.message.body.text + "it")
    await context.set_state(Reg.it_freza)
    await event.message.answer("Введите номер фрезы: ")


@router.message_created(Reg.it_freza)
async def visota_freza(event: MessageCreated, context: MemoryContext):
    await context.update_data(n_freza=event.message.body.text)
    await context.set_state(Reg.it_visota)
    await event.message.answer("Введите значение фрезы: ")


@router.message_created(Reg.it_visota)
async def itogo_freza(event: MessageCreated, context: MemoryContext):
    await context.update_data(n_visota=event.message.body.text.replace(",", "."))
    data = await context.get_data()
    await event.message.answer(value_freza(data['n_order'][:-2], data['n_freza'], data['n_visota']))
    await context.clear()


@router.message_callback(F.callback.payload == "сancel_standok")
async def cancel(event: MessageCallback, context: MemoryContext):
    await context.clear()
    await event.message.answer("Действие отменено", attachments=[kb_frezer])
    await event.answer()
