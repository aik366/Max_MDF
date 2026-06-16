from maxapi import Router, F
from maxapi.types import MessageCreated, Command, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters import BaseFilter
from app import keyboards as kb
from app import database as db
from fas import *
from config import *
import shutil, os
from pochta import gmail
from price.price_func import *
from time import strftime

router = Router()


class Reg(StatesGroup):
    number1 = State()
    number2 = State()
    data1 = State()
    data2 = State()
    our_order = State()
    ser_order = State()
    otchot = State()
    fasad = State()
    tolshina = State()
    plenka = State()


month, month_1 = strftime('%y'), str(int(strftime('%y')) - 1)
year, year_1 = strftime('%Y'), str(int(strftime('%Y')) - 1)


class MyFilter(BaseFilter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, event: MessageCreated) -> bool:
        s = event.message.body.text.replace(",", ".")
        if len(s) == 5 and s[:2].isdigit() and s[-2:].isdigit() and s[2] == '.' and int(s[:2]) < 32 and int(
                s[-2:]) < 13:
            return True
        return False


@router.message_created(Command('start'))
async def cmd_start(event: MessageCreated, context: MemoryContext):
    bot = event.bot
    print(event.message.sender.user_id, event.message.sender.full_name)
    await db.cmd_start_db(event.message.sender.user_id, event.message.sender.full_name)
    if not await db.db_check(event.message.sender.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.message.sender.full_name} {event.message.sender.user_id} Start")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")

    if await db.db_check(event.message.sender.user_id, "Admin"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_bot])
    elif await db.db_check(event.message.sender.user_id, "Vova"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_vova])
    elif await db.db_check(event.message.sender.user_id, "Shef"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_shef])
    elif await db.db_check(event.message.sender.user_id, "Ser"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_serdyuch])
    elif await db.db_check(event.message.sender.user_id, "Ellion"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_ellion])
    elif await db.db_check(event.message.sender.user_id, "Frezer"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_frezer])
    elif await db.db_check(event.message.sender.user_id, "None") or await db.db_check(event.message.sender.user_id,
                                                                                      "sklad"):
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_all_user])
    else:
        await event.message.answer(f"{event.message.sender.full_name} Это Фасад бот", attachments=[kb.kb_clent])

    await context.clear()


@router.message_created(Command("info"))
async def cmd_help(event: MessageCreated):
    bot = event.bot
    if await db.db_check(event.message.sender.user_id, "Admin"):
        with open('DATA/info.txt', 'r', encoding='utf-8') as f:
            await event.message.answer(f.read())
    else:
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.message.sender.full_name} {event.message.sender.user_id} info")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")
        await event.message.answer('тут пока пусто')


@router.message_created(F.message.body.text == "📨 Почта")
async def cmd_mail_yes_no(event: MessageCreated):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    buttons = [
        [CallbackButton(text="✅ Да, отправить", payload="to_send")],
        [CallbackButton(text="🔙 Отмена", payload="delete_cancel")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer('Отправить почту?', attachments=[payload])


@router.message_callback(F.callback.payload == "to_send")
async def cmd_mail(event: MessageCallback):
    bot = event.bot
    if not await db.db_check(event.callback.user.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'], text=str(event.callback.user.user_id) + " 📨 Почта")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")

    await event.message.answer(f'Почта отправлено {gmail.gmail_bimgor()}')
    await event.edit(attachments=[])
    await event.answer()


@router.message_callback(F.callback.payload == "delete_cancel")
async def del_mail(event: MessageCallback):
    await event.message.answer('Почта не отправлено')
    await event.edit(attachments=[])
    await event.answer()


@router.message_created(F.message.body.text == f"Обновить {year}")
async def cmd_program(event: MessageCreated, context: MemoryContext):
    bot = event.bot
    if await db.db_check(event.message.sender.user_id, "Admin"):
        shutil.copyfile(f'{put}{month}.RSB', 'DATA/22.txt')
        shutil.copyfile('DATA/22.txt', f'DATA/{month}_shef.txt')
        shutil.copyfile(put_ras, 'DATA/ras.txt')
        await event.message.answer(net_program())
    elif await db.db_check(event.message.sender.user_id, "Ser"):
        shutil.copyfile(f'{put}{month}.RSB', 'DATA/22.txt')
        try:
            await bot.send_message(chat_id=id_klient['bot'], text=str(event.message.sender.full_name) + " Обновить")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")
        await event.message.answer("Обновлено!!!")

    await context.clear()


@router.message_created(F.message.body.text == f"Обновить {year_1}")
async def cmd_program_2(event: MessageCreated, context: MemoryContext):
    if await db.db_check(event.message.sender.user_id, "Admin"):
        shutil.copyfile(f'{put}{month_1}.RSB', 'DATA/22.txt')
        await event.message.answer(net_program())
    elif await db.db_check(event.message.sender.user_id, "Ser"):
        shutil.copyfile(f'{put}{month_1}.RSB', 'DATA/22.txt')
        await event.message.answer("Обновлено!!!")

    await context.clear()


@router.message_created(F.message.body.text == "🔄 Обновить")
async def cmd_program_shef(event: MessageCreated, context: MemoryContext):
    bot = event.bot
    shutil.copyfile(f'{put}{month}.RSB', 'DATA/22.txt')
    shutil.copyfile('DATA/22.txt', f'DATA/{month}_shef.txt')
    shutil.copyfile(put_ras, 'DATA/ras.txt')
    try:
        await bot.send_message(chat_id=id_klient['bot'], text=f"{event.message.sender.full_name} Обновить")
    except Exception as e:
        print(f"[WARN] Не удалось отправить уведомление админу: {e}")
    await event.message.answer("Обновлено!!!")
    await context.clear()


@router.message_created(F.message.body.text == "📕 Долги")
async def cmd_dolgi(event: MessageCreated):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    in_kb = []
    for key, value in dolgi_user().items():
        in_kb.append([CallbackButton(text=f'{key} {value:,}', payload=f'###{key}')])

    payload = ButtonsPayload(buttons=in_kb).pack()
    await event.message.answer("📕 Долги", attachments=[payload])


@router.message_callback(F.callback.payload.startswith("###"))
async def dolgi_value(event: MessageCallback):
    bot = event.bot
    message_text = event.callback.payload[3:]
    duty_user = dolgi_user_2(message_text)
    call_one, call_two = '', ''
    total_one, total_two = 0, 0

    if len(duty_user[0]) > 0:
        key_one, call_one = duty_user[0], f'{message_text} Готовые\n'
        total_one = duty_user[2]
        for i in key_one:
            call_one += f'{i[0]}|{i[1]}|{i[2]:,} р.\n'
        call_one += f'итого: {total_one:,} руб.\n\n'

    if len(duty_user[1]) > 0:
        key_two, call_two = duty_user[1], f'{message_text} еще в работе\n'
        total_two = duty_user[3]
        for j in key_two:
            call_two += f'{j[0]}|{j[1]}|{j[2]:,} р.\n'
        call_two += f'итого: {total_two:,} руб.\n\n'

    await event.message.answer(f'{call_one}{call_two}Сумма: {(total_one + total_two):,} руб.')

    if not await db.db_check(event.callback.user.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.callback.user.full_name} Долги у {event.callback.payload[3:]}")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")

    await event.answer()


@router.message_created(F.message.body.text == "⚙️ Мои долги")
async def dolgi_one_value(event: MessageCreated):
    bot = event.bot
    message_text = await db.db_surname_check(event.message.sender.user_id)
    list1, list2, sum1, sum2 = dolgi_user_2(message_text)
    call_one, call_two = '', ''
    total_one, total_two = 0, 0

    if len(list1) > 0:
        key_one, call_one = list1, f'{message_text} Готовые\n'
        total_one = sum1
        for i in key_one:
            call_one += f'{i[0]}|{i[1]}|{i[2]:,} р.\n'
        call_one += f'итого: {total_one:,} руб.\n\n'

    if len(list2) > 0:
        key_two, call_two = list2, f'{message_text} еще в работе\n'
        total_two = sum2
        for j in key_two:
            call_two += f'{j[0]}|{j[1]}|{j[2]:,} р.\n'
        call_two += f'итого: {total_two:,} руб.\n\n'

    await event.message.answer(f'{call_one}{call_two}Сумма: {(total_one + total_two):,} руб.')

    if not await db.db_check(event.message.sender.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.message.sender.full_name} Долги у {message_text}")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")


dolgi_year = ""
my_dolgi_year = ""


@router.message_created(F.message.body.text == "⚙️ Мои заказы")
async def cmd_my_client_year(event: MessageCreated):
    await event.message.answer("Выберите год:", attachments=[kb.in_my_dolgi_year])


@router.message_callback(F.callback.payload.startswith("my_year"))
async def cmd_my_client(event: MessageCallback):
    bot = event.bot
    global my_dolgi_year
    my_dolgi_year = event.callback.payload
    message_text = await db.db_surname_check(event.callback.user.user_id)
    call_lst = client_user(message_text, my_dolgi_year[-2:]).split('\n')
    for j in range(0, len(call_lst), 130):
        tmp = '\n'.join(call_lst[j:j + 130])
        await event.message.answer(tmp)

    if not await db.db_check(event.callback.user.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.callback.user.full_name} Клиент {message_text}")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")

    await event.answer()


@router.message_created(F.message.body.text == "👨‍💼 Клиенты")
async def cmd_client_year(event: MessageCreated):
    await event.message.answer("Выберите год:", attachments=[kb.in_dolgi_year])


@router.message_callback(F.callback.payload.startswith("year"))
async def cmd_client_letter(event: MessageCallback):
    global dolgi_year
    dolgi_year = event.callback.payload
    await event.message.answer("Клиенты на букву:", attachments=[kb.in_letter])
    await event.answer()


@router.message_callback(F.callback.payload.startswith("%%%"))
async def cmd_client(event: MessageCallback):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    in_kb = []
    for key, value in client(event.callback.payload[-1], dolgi_year[-2:]).items():
        in_kb.append([CallbackButton(text=f'{key} {value:,}', payload=f'%#%{event.callback.payload[-1]}{key}')])

    payload = ButtonsPayload(buttons=in_kb).pack()

    if len(in_kb) != 0:
        await event.message.answer(f"Клиенты {dolgi_year[-4:]} год", attachments=[payload])
    else:
        await event.message.answer(f"Клиенты на букву {event.callback.payload[-1]} нет")

    await event.answer()


@router.message_callback(F.callback.payload.startswith("%#%"))
async def client_value(event: MessageCallback):
    bot = event.bot
    message_text = event.callback.payload[4:]
    call_lst = client_user(message_text, dolgi_year[-2:]).split('\n')
    for j in range(0, len(call_lst), 130):
        tmp = '\n'.join(call_lst[j:j + 130])
        await event.message.answer(tmp)

    if not await db.db_check(event.callback.user.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.callback.user.full_name} Клиент {message_text}")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")

    await event.answer()


zarplata_year = ""


@router.message_created(F.message.body.text == "💰 Зарплата")
async def cmd_zarplata_year(event: MessageCreated):
    await event.message.answer("Выберите год:", attachments=[kb.in_zarplata_year])


@router.message_callback(F.callback.payload.startswith("zar_year"))
async def cmd_zarplata(event: MessageCallback):
    global zarplata_year
    zarplata_year = event.callback.payload
    await event.message.answer(f"💸 Зарплата за {zarplata_year[-4:]} год", attachments=[kb.in_mesyac])
    await event.answer()


@router.message_callback(F.callback.payload.startswith("!!!"))
async def zorplata_value(event: MessageCallback):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    in_zarp = [
        [CallbackButton(text='Подробно', payload=f'&&&{event.callback.payload[3:]}')],
        [CallbackButton(text='Обратка', payload=f'^^^{event.callback.payload[3:]}')]
    ]
    payload = ButtonsPayload(buttons=in_zarp).pack()

    await event.message.answer(zarplata(event.callback.payload[3:], zarplata_year[-2:])[0], attachments=[payload])
    await event.answer()


@router.message_callback(F.callback.payload.startswith("&&&"))
async def zorplata_podrobno_value(event: MessageCallback):
    call_list = zarplata(event.callback.payload[3:], zarplata_year[-2:])[1].split('\n')
    for j in range(0, len(call_list), 130):
        tmp = '\n'.join(call_list[j:j + 130])
        await event.message.answer(tmp)
    await event.answer()


@router.message_callback(F.callback.payload.startswith("^^^"))
async def zorplata_obratka(event: MessageCallback):
    call_list = zarplata(event.callback.payload[3:], zarplata_year[-2:])[2]
    await event.message.answer(call_list)
    await event.answer()


@router.message_created(F.message.body.text == "🚻 Сердюченко")
async def reg_one(event: MessageCreated):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    fms_list = [
        [CallbackButton(text="🔢 По номеру заказа?", payload="По номеру заказа")],
        [CallbackButton(text="📅 По дате заказа?", payload="По дате заказа")]
    ]
    fms_payload = ButtonsPayload(buttons=fms_list).pack()
    await event.message.answer("Сердюченко", attachments=[fms_payload])


@router.message_callback(F.callback.payload == "По номеру заказа")
async def reg_one_cb(event: MessageCallback, context: MemoryContext):
    await context.set_state(Reg.number1)
    await event.message.answer("Введите начальный\nномер заказа")
    await event.answer()


@router.message_created(Reg.number1, F.message.body.text.isdigit())
async def reg_two(event: MessageCreated, context: MemoryContext):
    if len(event.message.body.text) == 4:
        await context.update_data(number1=event.message.body.text)
        await context.set_state(Reg.number2)
        await event.message.answer("Введите Конечный\nномер заказа")
    else:
        await event.message.answer("Только 4 цифры\nВведите начальный\nномер заказа")


@router.message_created(Reg.number2, F.message.body.text.isdigit())
async def reg_three(event: MessageCreated, context: MemoryContext):
    if len(event.message.body.text) == 4:
        await context.update_data(number2=event.message.body.text)
        data = await context.get_data()
        number_1, number_2 = data["number1"], data["number2"]
        summ = dolgi_serdyuch(number_1, number_2)[0]

        from maxapi.types.attachments.buttons import CallbackButton
        from maxapi.types.attachments.attachment import ButtonsPayload

        in_dolgi = [
            [CallbackButton(text=f'{number_1} --> {number_2} Сумма: {summ:,}', payload=f"NMB{number_1} {number_2}")]]
        payload = ButtonsPayload(buttons=in_dolgi).pack()

        await event.message.answer("Сердюченко", attachments=[payload])
        await context.clear()
    else:
        await event.message.answer("Только 4 цифры\nВведите Конечный\nномер заказа")


@router.message_callback(F.callback.payload.startswith("NMB"))
async def serdyuch_value(event: MessageCallback):
    number_1, number_2 = event.callback.payload[3:7], event.callback.payload[-4:]
    summ, lst = dolgi_serdyuch(number_1, number_2)[0], '\n'.join(dolgi_serdyuch(number_1, number_2)[1])
    lst += f'\n\nитого: {summ:,}'
    call_lst = lst.split('\n')
    for j in range(0, len(call_lst), 130):
        tmp = '\n'.join(call_lst[j:j + 130])
        await event.message.answer(tmp)
    await event.answer()


@router.message_callback(F.callback.payload == "По дате заказа")
async def reg_data_one(event: MessageCallback, context: MemoryContext):
    await context.set_state(Reg.data1)
    await event.message.answer(f"Введите начальную дату заказа в \nформате день . месяц(пример 03.04)")
    await event.answer()


@router.message_created(Reg.data1, MyFilter(""))
async def reg_data_two(event: MessageCreated, context: MemoryContext):
    await context.update_data(data1=event.message.body.text.replace(",", "."))
    await context.set_state(Reg.data2)
    await event.message.answer(f"Введите Конечную дату заказа в \nформате день . месяц(пример 03.04)")


@router.message_created(Reg.data1)
async def reg_two_err(event: MessageCreated):
    await event.message.answer(f"Ошибка!!!\nВведите начальную дату заказа в \nформате день . месяц(пример 03.04)")


@router.message_created(Reg.data2, MyFilter(""))
async def reg_data_three(event: MessageCreated, context: MemoryContext):
    await context.update_data(data2=event.message.body.text.replace(",", "."))
    data = await context.get_data()
    data_1, data_2 = data["data1"], data["data2"]
    summ = dolgi_ser_data(data_1, data_2)[0]

    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    in_dolgi = [[CallbackButton(text=f'{data_1} --> {data_2} Сумма: {summ:,}', payload=f"DTA{data_1} {data_2}")]]
    payload = ButtonsPayload(buttons=in_dolgi).pack()

    await event.message.answer("Сердюченко", attachments=[payload])
    await context.clear()


@router.message_created(Reg.data2)
async def reg_two_err2(event: MessageCreated):
    await event.message.answer(f"Ошибка!!!\nВведите Конечную дату заказа в \nформате день . месяц(пример 03.04)")


@router.message_callback(F.callback.payload.startswith("DTA"))
async def serdyuch_data_value(event: MessageCallback):
    data_1, data_2 = event.callback.payload[3:8], event.callback.payload[-5:]
    summ, lst = dolgi_ser_data(data_1, data_2)[0], '\n'.join(dolgi_ser_data(data_1, data_2)[1])
    lst += f'\n\nитого: {summ:,}'
    call_lst = lst.split('\n')
    for j in range(0, len(call_lst), 130):
        tmp = '\n'.join(call_lst[j:j + 130])
        await event.message.answer(tmp)
    await event.answer()


@router.message_created(F.message.body.text == "📝 Отчет")
async def cmd_rasxodi_2(event: MessageCreated):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    fms_list = [
        [CallbackButton(text=f"📆 Отчет за {today_func()}", payload="otchet za segodnya")],
        [CallbackButton(text="📆 Отчет по дате", payload="Отчет по дате")]
    ]
    fms_payload = ButtonsPayload(buttons=fms_list).pack()
    await event.message.answer("Отчет", attachments=[fms_payload])


@router.message_callback(F.callback.payload == "otchet za segodnya")
async def call_otchot(event: MessageCallback):
    bot = event.bot
    await event.message.answer(otchet(today_func()))
    if event.callback.user.user_id != id_klient['bot']:
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.callback.user.full_name} Отчет за {today_func()}")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")
    await event.answer()


@router.message_callback(F.callback.payload == "Отчет по дате")
async def reg_one_otchot(event: MessageCallback, context: MemoryContext):
    await context.set_state(Reg.otchot)
    await event.message.answer(f"Введите дату в формате\nдень . месяц(пример 04.02)")
    await event.answer()


@router.message_created(Reg.otchot, MyFilter(""))
async def reg_three_otchot(event: MessageCreated, context: MemoryContext):
    bot = event.bot
    await context.update_data(otchot=event.message.body.text.replace(",", "."))
    data = await context.get_data()
    await event.message.answer(otchet(data["otchot"]))
    if not await db.db_check(event.message.sender.user_id, "Admin"):
        try:
            await bot.send_message(chat_id=id_klient['bot'],
                                   text=f"{event.message.sender.full_name} Отчет за {data['otchot']}")
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление админу: {e}")
    await context.clear()


@router.message_created(Reg.otchot)
async def reg_two_err3(event: MessageCreated):
    await event.message.answer(f"Ошибка!!!\nВведите дату в формате\nдень . месяц(пример 04.02)")


@router.message_created(F.message.body.text == "🚪 Фасады")
async def cmd_ris_valyut(event: MessageCreated):
    await event.message.answer("Фасады", attachments=[kb.in_risunok])


@router.message_callback(F.callback.payload.startswith("$"))
async def ris_value(event: MessageCallback):
    bot = event.bot
    from maxapi.types.input_media import InputMedia
    for i in os.listdir(f'./images/{event.callback.payload[1:]}'):
        img = InputMedia(path=f'images/{event.callback.payload[1:]}/{i}')
        attachment = await bot.upload_media(img)
        await event.message.answer(text=i.split('.')[0], attachments=[attachment])
    await event.answer()


@router.message_created(F.message.body.text == "❗Инфо по заказу")
async def info_order(event: MessageCreated):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    fms_list = [
        [CallbackButton(text="🔢 Наш номер заказа", payload="Наш номер заказа")],
        [CallbackButton(text="🔢 Номер Сердюченко", payload="Номер Сердюченко")]
    ]
    fms_payload = ButtonsPayload(buttons=fms_list).pack()
    await event.message.answer("Наш или Сердюченко?", attachments=[fms_payload])


@router.message_callback(F.callback.payload == "Наш номер заказа")
async def reg_one_order_1(event: MessageCallback, context: MemoryContext):
    await context.set_state(Reg.our_order)
    await event.message.answer("Введите наш номер заказа")
    await event.answer()


@router.message_created(Reg.our_order, F.message.body.text.isdigit())
async def reg_three_order_1(event: MessageCreated, context: MemoryContext):
    if len(event.message.body.text) == 4:
        await context.update_data(our_order=event.message.body.text)
        data = await context.get_data()
        await event.message.answer(f"<pre>{serdyuch(data['our_order'])}</pre>")
        await context.clear()
    else:
        await event.message.answer("Ошибка!!!\nТолько 4 цифры")


@router.message_callback(F.callback.payload == "Номер Сердюченко")
async def reg_one_order_2(event: MessageCallback, context: MemoryContext):
    await context.set_state(Reg.ser_order)
    await event.message.answer("Введите номер Сердюченко")
    await event.answer()


@router.message_created(Reg.ser_order, F.message.body.text.isdigit())
async def reg_three_order_2(event: MessageCreated, context: MemoryContext):
    if len(event.message.body.text) == 4:
        await context.update_data(ser_order=event.message.body.text)
        data = await context.get_data()
        ser_txt = serd_nomer_4(data["ser_order"], "Сердюченко")
        await event.message.answer(f"<pre>{serdyuch(ser_txt)}</pre>")
        await context.clear()
    else:
        await event.message.answer("Ошибка!!!\nТолько 4 цифры")


@router.message_created(F.message.body.text == "🪚 Раскрой")
async def cmd_raskroy(event: MessageCreated):
    call_lst = raskroy().split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')


@router.message_created(F.message.body.text == "🪚 Раскрой/ост.")
async def cmd_raskroy_ost(event: MessageCreated):
    call_lst = raskroy_ost().split('\n')
    for j in range(0, len(call_lst), 120):
        tmp = '\n'.join(call_lst[j:j + 120])
        await event.message.answer(f'{tmp}')


@router.message_created(F.message.body.text == "🪚 Раскрой/зар.")
async def cmd_raskroy_zar(event: MessageCreated):
    call_lst = raskroy_zarplata().split('\n')
    for j in range(0, len(call_lst), 120):
        tmp = '\n'.join(call_lst[j:j + 120])
        await event.message.answer(f'{tmp}')


@router.message_created(F.message.body.text == "🕹 Фрезер")
async def cmd_frezar(event: MessageCreated):
    call_lst = frezer().split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')


@router.message_created(F.message.body.text == "⚙️ Пресс")
async def cmd_press(event: MessageCreated):
    call_lst = press().split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')


@router.message_created(F.message.body.text == "💷 Стоимость")
async def cmd_price(event: MessageCreated, context: MemoryContext):
    await context.set_state(Reg.fasad)
    await event.message.answer("Выберите форму фасада", attachments=[kb.in_ris_price])


@router.message_callback(Reg.fasad, F.callback.payload.startswith("fasad"))
async def reg_one_price(event: MessageCallback, context: MemoryContext):
    await context.update_data(fasad=event.callback.payload)
    await context.set_state(Reg.tolshina)

    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    fms_list = [[
        CallbackButton(text="10mm", payload="10_tolshina"),
        CallbackButton(text="16mm", payload="16_tolshina"),
        CallbackButton(text="19mm", payload="19_tolshina"),
        CallbackButton(text="22mm", payload="22_tolshina"),
        CallbackButton(text="32mm", payload="32_tolshina")
    ]]
    fms_payload = ButtonsPayload(buttons=fms_list).pack()

    await event.message.answer("Выберите толщину фасада", attachments=[fms_payload])
    await event.answer()


@router.message_callback(Reg.tolshina, F.callback.payload.endswith("tolshina"))
async def reg_two_price(event: MessageCallback, context: MemoryContext):
    await context.update_data(tolshina=event.callback.payload)
    await context.set_state(Reg.plenka)
    await event.message.answer("Выберите группу пленки", attachments=[kb.in_group_pl])
    await event.answer()


@router.message_callback(Reg.plenka, F.callback.payload.startswith("group"))
async def reg_tree_price(event: MessageCallback, context: MemoryContext):
    await context.update_data(plenka=event.callback.payload)
    data = await context.get_data()
    plen_ka, tol_shina, fas_ad = int(data['plenka'][5:]), data['tolshina'][:2], data['fasad'][5:]
    await event.message.answer(f"Форма фасад № {fas_ad}\nТолщина фасада {tol_shina}мм\nГруппа пленки {plen_ka}\n\n"
                               f"Стоимость {price_summ(plen_ka, tol_shina, fas_ad)} руб. за кв.м")
    await event.answer()


@router.message_created(F.message.body.text == '🟧 Пленки')
async def cmd_plenki(event: MessageCreated):
    from maxapi.types.attachments.buttons import CallbackButton
    from maxapi.types.attachments.attachment import ButtonsPayload

    fms_list = [[
        CallbackButton(text="по группам", payload="по группам"),
        CallbackButton(text="по номеру", payload="по номеру"),
        CallbackButton(text="по названию", payload="по названию")
    ]]
    fms_payload = ButtonsPayload(buttons=fms_list).pack()
    await event.message.answer("Как сортировать пленки", attachments=[fms_payload])


@router.message_callback(F.callback.payload == 'по номеру')
async def po_nomeru(event: MessageCallback):
    call_lst = print_plenka_number().split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')
    await event.answer()


@router.message_callback(F.callback.payload == 'по названию')
async def po_nazvaniu(event: MessageCallback):
    call_lst = print_plenka_sort().split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')
    await event.answer()


@router.message_callback(F.callback.payload == 'по группам')
async def po_grupam(event: MessageCallback):
    await event.message.answer("Выберите группу пленки", attachments=[kb.in_group_sort])
    await event.answer()


@router.message_callback(F.callback.payload.startswith('sort'))
async def reg_tree_price_sort(event: MessageCallback):
    call_lst = print_plenka_group(event.callback.payload[4:]).split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')
    await event.answer()


@router.message_created(F.message.body.text == '📊 Статистика')
async def statics(event: MessageCreated):
    await event.message.answer("Выберите 👇", attachments=[kb.in_static_plenka])


@router.message_callback(F.callback.payload == 'static_plenki')
async def in_statics_pl(event: MessageCallback):
    call_lst = statistics_plenka().split('\n')
    for j in range(0, len(call_lst), 100):
        tmp = '\n'.join(call_lst[j:j + 100])
        await event.message.answer(f'{tmp}')
    await event.answer()


@router.message_callback(F.callback.payload == 'static_fasad')
async def in_statics_fs(event: MessageCallback):
    await event.message.answer(f'{statistics_fasad()}')
    await event.answer()


@router.message_callback(F.callback.payload == 'static_mdf')
async def in_statics_mdf(event: MessageCallback):
    await event.message.answer(f'{statistics_mdf()}')
    await event.answer()
