from maxapi import Router, Bot, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.attachments.attachment import ButtonsPayload
from app.nc_stanok import podkladka, speed_change, add_nc_freza
from app.ss_stanok import add_ss_freza
from app.it_stanok import add_it_freza
from app import keyboards as kb

router = Router()


class Reg(StatesGroup):
    n_order = State()
    podklad = State()
    num_order = State()
    num_freza = State()
    speed_freza = State()
    order_num = State()
    stanok = State()


@router.message_created(F.message.body.text == "nc_станок")
async def number_order(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Это nc станок", attachments=[kb.kb_frezer_nc])


@router.message_created(F.message.body.text == "↩️ Назад")
async def back_to_start(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Начало", attachments=[kb.kb_frezer])


@router.message_created(F.message.body.text == "Подклад")
async def start_podklad(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Reg.n_order)
    await event.message.answer("Введите номер заказа: ")


@router.message_created(Reg.n_order)
async def tol_podkladki(event: MessageCreated, context: MemoryContext):
    await context.update_data(n_order=event.message.body.text + "nc")
    await context.set_state(Reg.podklad)
    await event.message.answer("Введите толщину подкладки: ")


@router.message_created(Reg.podklad)
async def podklad(event: MessageCreated, context: MemoryContext):
    await context.update_data(podklad=event.message.body.text)
    data = await context.get_data()
    await event.message.answer(f"{podkladka(data['n_order'], data['podklad'])}")
    await context.clear()


@router.message_created(F.message.body.text == "Подача")
async def start_podacha(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Reg.num_order)
    await event.message.answer("Введите номер заказа: ")


@router.message_created(Reg.num_order)
async def num_freza(event: MessageCreated, context: MemoryContext):
    await context.update_data(num_order=event.message.body.text + "nc")
    await context.set_state(Reg.num_freza)
    await event.message.answer("Введите номер фрезы: ")


@router.message_created(Reg.num_freza)
async def speed_podachi(event: MessageCreated, context: MemoryContext):
    await context.update_data(num_freza=event.message.body.text)
    await context.set_state(Reg.speed_freza)
    await event.message.answer("Введите скорость подачи: ")


@router.message_created(Reg.speed_freza)
async def podacha(event: MessageCreated, context: MemoryContext):
    await context.update_data(speed_freza=event.message.body.text)
    data = await context.get_data()
    await event.message.answer(f"{speed_change(data['num_order'], data['num_freza'], data['speed_freza'])}")
    await context.clear()


@router.message_created(F.message.body.text == "+132 фреза")
async def order_num(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Reg.order_num)
    await event.message.answer("Введите номер заказа: ")


@router.message_created(Reg.order_num)
async def stanok(event: MessageCreated, context: MemoryContext):
    await context.update_data(order_num=event.message.body.text)
    await context.set_state(Reg.stanok)

    buttons = [
        [CallbackButton(text="ss", payload="ss_stanok"),
         CallbackButton(text="nc", payload="nc_stanok"),
         CallbackButton(text="it", payload="it_stanok")],
        [CallbackButton(text="✖отмена", payload="сancel_standok")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите станок: ", attachments=[payload])


@router.message_callback(Reg.stanok, F.callback.payload.endswith("stanok"))
async def arkhive_order(event: MessageCallback, context: MemoryContext):
    await context.update_data(stanok=event.callback.payload[:2])
    data = await context.get_data()

    await event.message.answer(f"Номер заказа: {data['order_num']}\nСтанок: {data['stanok']}_станок",
                               attachments=[kb.kb_frezer])

    if data['stanok'] == "ss":
        await event.message.answer(f"{add_ss_freza(data['order_num'])}")
    elif data['stanok'] == "nc":
        await event.message.answer(f"{add_nc_freza(data['order_num'])}")
    elif data['stanok'] == "it":
        await event.message.answer(f"{add_it_freza(data['order_num'])}")

    await context.clear()
    await event.answer()


@router.message_callback(F.callback.payload == "сancel_standok")
async def cancel(event: MessageCallback, context: MemoryContext):
    await context.clear()
    await event.message.answer("Действие отменено", attachments=[kb.kb_frezer])
    await event.answer()