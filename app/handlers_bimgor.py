import asyncio
from maxapi import Router, Bot, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types.input_media import InputMedia
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.attachments.attachment import ButtonsPayload
from app import database as db
from app import keyboards as kb
from fas import *
from config import *
from distutils.dir_util import copy_tree
import shutil, pyautogui, psutil, os, zipfile
from fasadit import fasad_italiya

router = Router()


class Fasad(StatesGroup):
    number = State()
    tolshina = State()
    kray = State()
    freza = State()
    radius = State()
    risunok = State()
    comment = State()
    zakaz = State()
    dimensions = State()
    dir_del = State()
    zak_az = []


@router.message_created(F.message.body.text == "Срочность")
async def cmd_srochno(event: MessageCreated):
    await event.message.answer(srochnost())
    await event.message.answer(srochnost_bud())


@router.message_created(F.message.body.text == "💵 Курсы валют")
async def cmd_kursi_valyut(event: MessageCreated):
    await event.message.answer(currency())


@router.message_created(F.message.body.text == "Заказы")
async def cmd_zakazi(event: MessageCreated):
    f = open('DATA/n_zak.txt', 'r').read().split('|')
    for i in range(len(f) - 1):
        # Примечание: так как kb.kb_in теперь упакован в ButtonsPayload,
        # мы отправляем только кнопку заказа. Если нужна полная клавиатура,
        # нужно экспортировать сырой список кнопок из keyboards.py.
        btn = CallbackButton(text='⚙ ' + f[i] + ' ⚙', payload=f'zakaz{f[i]}')
        payload = ButtonsPayload(buttons=[[btn]]).pack()
        await event.message.answer(f"<pre>{serdyuch(f[i])}</pre>", attachments=[payload])


@router.message_created(F.message.body.text == "Доп. кнопки")
async def cmd_fail_skrin(event: MessageCreated):
    await event.message.answer("Доп-кнопки", attachments=[kb.dop_kn])


@router.message_callback(F.callback.payload == "papki_value")
async def send_papki_value(event: MessageCallback):
    ss, nc, it = 'ss станок: ', 'nc станок: ', 'it станок: '
    for i in os.listdir('.\\ss'):
        ss += i[:4] + '|'
    for i in os.listdir('.\\nc'):
        nc += i[:4] + '|'
    for i in os.listdir('.\\it'):
        it += i[:4] + '|'
    await event.message.answer(f'{ss}\n{nc}\n{it}')
    await event.message.answer('zak_az: {}'.format('|'.join(Fasad.zak_az)))
    await event.answer()


@router.message_callback(F.callback.payload == "del_value")
async def send_del_value(event: MessageCallback):
    os.system('rmdir /S /Q "{}"'.format('ss'))
    os.system('rmdir /S /Q "{}"'.format('nc'))
    os.system('rmdir /S /Q "{}"'.format('it'))
    os.makedirs('ss')
    os.makedirs('nc')
    os.makedirs('it')
    await event.message.answer("Процесс удаления завершен")
    await event.answer()


@router.message_callback(F.callback.payload == "copyit_value_it")
async def send_copyit_value_tt(event: MessageCallback):
    g = ''
    if os.path.exists(put_555it):
        for i in os.listdir('.\\it'):
            copy_tree('it/' + i, put_555it + "/" + i)
            g += i[:4] + '|'
        await event.message.answer('{} \nкопирования it станка завершен'.format(g))
    else:
        await event.message.answer('it stanok off')
    await event.answer()


@router.message_callback(F.callback.payload == "copync_value_nc")
async def send_copync_value_ss(event: MessageCallback):
    g = ''
    if os.path.exists(put_555nc):
        for i in os.listdir('.\\nc'):
            copy_tree('nc/' + i, put_555nc + "/" + i)
            g += i[:4] + '|'
        await event.message.answer('{} \nкопирования nc станка завершен'.format(g))
    else:
        await event.message.answer('nc stanok off')
    await event.answer()


@router.message_callback(F.callback.payload == "copyss_value_ss")
async def send_copyss_value_nc(event: MessageCallback):
    if os.path.exists(put_555ss):
        for i in os.listdir('.\\ss'):
            copy_tree('ss/' + i, put_555ss + "/" + i)
            if i[:4] not in Fasad.zak_az:
                Fasad.zak_az.append(i[:4])
        await event.message.answer('{} \nкопирования ss станка завершен'.format('|'.join(Fasad.zak_az)))
    else:
        await event.message.answer('ss stanok off')
    await event.answer()


@router.message_callback(F.callback.payload == "copy_value")
async def send_copy_value(event: MessageCallback):
    if os.path.exists(put_555it):
        copy_tree(put_it, put_555it)
        await event.message.answer("копирования it станка завершен")
    else:
        await event.message.answer('it stanok off')

    if os.path.exists(put_555nc):
        copy_tree(put_nc, put_555nc)
        await event.message.answer("копирования nc станка завершен")
    else:
        await event.message.answer('nc stanok off')

    if os.path.exists(put_555ss):
        copy_tree(put_ss, put_555ss)
        for i in os.listdir(put_ss):
            if len(i) == 5 and i[-1] == 'h' and i[:4] not in Fasad.zak_az:
                Fasad.zak_az.append(i[:4])
        await event.message.answer("{} копирования ss станка завершен".format('|'.join(Fasad.zak_az)))
    else:
        await event.message.answer('ss stanok off')
    await event.answer()


@router.message_callback(F.callback.payload == "zk_Del_value")
async def send_zk_del_value(event: MessageCallback):
    for i in os.listdir(put_ss):
        if len(i) > 4 and i[3].isdigit():
            os.system('rmdir /S /Q "{}"'.format(put_ss + i))
    for i in os.listdir(put_nc):
        if len(i) > 4 and i[3].isdigit():
            os.system('rmdir /S /Q "{}"'.format(put_nc + i))
    for i in os.listdir(put_it):
        if len(i) > 4 and i[3].isdigit():
            os.system('rmdir /S /Q "{}"'.format(put_it + i))
    await event.message.answer(f"Процесс удаления завершен")
    await event.answer()


@router.message_callback(F.callback.payload == "otmetka_value")
async def otmetka_value(event: MessageCallback):
    shutil.copyfile(f'{put}{month}.RSB', 'DATA/22.txt')
    await event.message.answer("Обновлено!!!", otmetka_program(Fasad.zak_az))
    Fasad.zak_az.clear()
    await event.answer()


@router.message_callback(F.callback.payload == "proc_value")
async def send_proc_value(event: MessageCallback):
    temp_true = "FasadMDF.exe" in (p.name() for p in psutil.process_iter())
    await event.message.answer(str(temp_true))
    await event.answer()


@router.message_callback(F.callback.payload == "proc_otmetka_value")
async def send_proc_otmetka_value(event: MessageCallback):
    while True:
        temp_true = "FasadMDF.exe" in (p.name() for p in psutil.process_iter())
        if not temp_true:
            shutil.copyfile(f'{put}{month}.RSB', 'DATA/22.txt')
            await event.message.answer("Обновлено!!!", otmetka_program(Fasad.zak_az))
            Fasad.zak_az.clear()
            break
        await asyncio.sleep(20)


@router.message_callback(F.callback.payload == "skrin_value")
async def send_skrin_value(event: MessageCallback, bot: Bot):
    pyautogui.screenshot('DATA/33.png')
    cat = InputMedia(path='DATA/33.png')
    attachment = await bot.upload_media(cat)
    await event.message.answer(attachments=[attachment])
    await event.answer()


@router.message_callback(F.callback.payload == "fail_value")
async def send_fail_value(event: MessageCallback, bot: Bot):
    shutil.copyfile(f"{put}{month}.RSB", f"files/Заказы{month}.RSB")
    shutil.copyfile(f"{put_ras}", f"files/расходы.RSB")
    for i in os.listdir(f'./files/'):
        file = InputMedia(path=f'files/{i}')
        attachment = await bot.upload_media(file)
        await event.message.answer(text=i, attachments=[attachment])
    await event.answer()


@router.message_created()
async def get_user_document(event: MessageCreated, bot: Bot):
    if not event.message.attachments:
        return
    att = event.message.attachments[0]
    if not hasattr(att, 'file_name'):
        return

    file_id = att.file_id
    file_name = att.file_name
    await event.message.answer('Загрузка...')

    # Примечание: метод скачивания может называться bot.download или bot.download_media
    try:
        await bot.download(file_id, "DATA/temp_file")
    except Exception:
        pass

    if file_name.endswith('.zip'):
        shutil.move("DATA/temp_file", "DATA/file.zip")
        with zipfile.ZipFile("DATA/file.zip", 'r') as zip_ref:
            for i in zip_ref.namelist():
                if len(i) > 14:
                    if i[7] == 'h':
                        zip_ref.extract(i, path=put_ss_zip)
                    elif i[7] == 'n':
                        zip_ref.extract(i, path=put_nc_zip)
                    elif i[7] == 'i':
                        zip_ref.extract(i, path=put_it_zip)
    else:
        shutil.move("DATA/temp_file", "DATA/text.txt")
        await event.message.answer(f"{file_name} скачан")


@router.message_callback(F.callback.payload == "temp_value")
async def send_temp_value(event: MessageCallback):
    shutil.copyfile('DATA/text.txt', 'DATA/22.txt')
    await event.message.answer("Временно обновлено!")
    await event.answer()


bez_frez = [0] * 11


@router.message_callback(F.callback.payload == "value_156")
async def value_157(event: MessageCallback):
    await event.message.answer("Без расширения")
    bez_frez[0] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_144_1")
async def value_144_1(event: MessageCallback):
    await event.message.answer("Без 144_1")
    bez_frez[1] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_144_2")
async def value_144_2(event: MessageCallback):
    await event.message.answer("Без 144_2")
    bez_frez[2] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_144_3")
async def value_144_3(event: MessageCallback):
    await event.message.answer("Без 144_3")
    bez_frez[3] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_45")
async def value_pod_45(event: MessageCallback):
    await event.message.answer("под 45")
    bez_frez[4] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_136_1")
async def value_136_1(event: MessageCallback):
    await event.message.answer("Без 136_1")
    bez_frez[5] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_136_2")
async def value_136_2(event: MessageCallback):
    await event.message.answer("Без 136_2")
    bez_frez[6] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_136_3")
async def value_136_3(event: MessageCallback):
    await event.message.answer("Без 136_3")
    bez_frez[7] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_bez_xdf")
async def value_bez_xdf(event: MessageCallback):
    await event.message.answer("Без хдф")
    bez_frez[8] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_ramy_45")
async def value_ramy(event: MessageCallback):
    await event.message.answer("стандартная ширина рамки")
    bez_frez[9] = 1
    await event.answer()


@router.message_callback(F.callback.payload == "value_92")
async def value_pod_92(event: MessageCallback):
    await event.message.answer("под 92")
    bez_frez[10] = 1
    await event.answer()


@router.message_callback(F.callback.payload.startswith('zakaz'))
async def cmd_zaks(event: MessageCallback):
    await event.message.answer(f'Заказ {event.callback.payload[-4:]} Готов',
                               fasad_italiya(event.callback.payload[-4:], '5',
                                             bez_frez[0], bez_frez[1], bez_frez[2],
                                             bez_frez[3], bez_frez[4], bez_frez[5],
                                             bez_frez[6], bez_frez[7], bez_frez[8],
                                             bez_frez[9], bez_frez[10]))
    for i in range(11):
        bez_frez[i] = 0
    await event.answer()


@router.message_callback(F.callback.payload == "do_facade")
async def fasad_number_cb(event: MessageCallback, context: MemoryContext):
    await context.set_state(Fasad.zakaz)
    await context.update_data(fasad_line=[])
    await event.message.answer("Выберите номер заказа")
    await event.answer()


@router.message_created(Fasad.zakaz)
async def fasad_number_msg(event: MessageCreated, context: MemoryContext):
    await context.update_data(zakaz=event.message.body.text)
    await context.set_state(Fasad.number)
    await event.message.answer("Выберите номер фасада", attachments=[kb.in_ris_facade])


@router.message_callback(Fasad.number, F.callback.payload.startswith("facade"))
async def fasad_tolshina(event: MessageCallback, context: MemoryContext):
    await context.update_data(number=event.callback.payload[6:])
    await context.set_state(Fasad.tolshina)
    buttons = [[
        CallbackButton(text="10mm", payload="10_tolshina"),
        CallbackButton(text="16mm", payload="16_tolshina"),
        CallbackButton(text="19mm", payload="19_tolshina"),
        CallbackButton(text="22mm", payload="22_tolshina"),
        CallbackButton(text="32mm", payload="32_tolshina")
    ]]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите толщину фасада", attachments=[payload])
    await event.answer()


@router.message_callback(Fasad.tolshina, F.callback.payload.endswith("tolshina"))
async def fasad_kray(event: MessageCallback, context: MemoryContext):
    await context.update_data(tolshina=event.callback.payload[:2])
    await context.set_state(Fasad.kray)
    buttons = [
        [CallbackButton(text="11", payload="11_kray"), CallbackButton(text="12", payload="12_kray"),
         CallbackButton(text="13", payload="13_kray"), CallbackButton(text="14", payload="14_kray"),
         CallbackButton(text="15", payload="15_kray")],
        [CallbackButton(text="16", payload="16_kray"), CallbackButton(text="17", payload="17_kray"),
         CallbackButton(text="18", payload="18_kray"), CallbackButton(text="19", payload="19_kray"),
         CallbackButton(text="20", payload="20_kray")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите край фасада", attachments=[payload])
    await event.answer()


@router.message_callback(Fasad.kray, F.callback.payload.endswith("kray"))
async def fasad_freza(event: MessageCallback, context: MemoryContext):
    await context.update_data(kray=event.callback.payload[:2])
    await context.set_state(Fasad.freza)
    buttons = [
        [CallbackButton(text="21", payload="21_freza"), CallbackButton(text="22", payload="22_freza"),
         CallbackButton(text="23", payload="23_freza"), CallbackButton(text="24", payload="24_freza"),
         CallbackButton(text="26", payload="26_freza")],
        [CallbackButton(text="28", payload="28_freza"), CallbackButton(text="29", payload="29_freza"),
         CallbackButton(text="30", payload="30_freza"), CallbackButton(text="БФ", payload="БФ_freza"),
         CallbackButton(text="ФП", payload="ФП_freza")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите фрезу фасада", attachments=[payload])
    await event.answer()


@router.message_callback(Fasad.freza, F.callback.payload.endswith("freza"))
async def fasad_radius(event: MessageCallback, context: MemoryContext):
    await context.update_data(freza=event.callback.payload[:2])
    await context.set_state(Fasad.radius)
    buttons = [[
        CallbackButton(text="R1", payload="R1_Radius"), CallbackButton(text="R2", payload="R2_Radius"),
        CallbackButton(text="R3", payload="R3_Radius"), CallbackButton(text="R4", payload="R4_Radius"),
        CallbackButton(text="R5", payload="R5_Radius")
    ]]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Выберите радиус фасада", attachments=[payload])
    await event.answer()


@router.message_callback(Fasad.radius, F.callback.payload.endswith("Radius"))
async def fasad_risunok(event: MessageCallback, context: MemoryContext):
    await context.update_data(radius=event.callback.payload[:2])
    await context.set_state(Fasad.risunok)
    await event.message.answer("Выберите вид фасада", attachments=[kb.in_vid_facade])
    await event.answer()


@router.message_callback(Fasad.risunok, F.callback.payload.endswith("_Ris"))
async def fasad_all_ris(event: MessageCallback, context: MemoryContext):
    await context.update_data(risunok=event.callback.payload[:-4])
    await context.set_state(Fasad.comment)
    buttons = [[
        CallbackButton(text="нет", payload="_com"),
        CallbackButton(text="4 окошек", payload="4_com"),
        CallbackButton(text="8 окошек", payload="8_com")
    ]]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer("Пишите примечания к заказу", attachments=[payload])
    await event.answer()


@router.message_callback(Fasad.comment, F.callback.payload.endswith("_com"))
async def fasad_zakaz(event: MessageCallback, context: MemoryContext):
    await context.update_data(comment=event.callback.payload[:-4])
    await context.set_state(Fasad.dimensions)
    await event.message.answer("Пишите размеры через пробел\nили нажмите на отмена")
    await event.answer()


@router.message_created(Fasad.dimensions)
async def fasad_all_msg(event: MessageCreated, context: MemoryContext):
    text = event.message.body.text
    await context.update_data(dimensions=text)
    d = await context.get_data()
    dlina, shirina = text.split()
    d['fasad_line'] += [
        f"{dlina}.{shirina}.{d['number']}.{d['kray']}.{d['freza']}.{d['risunok']}.{d['tolshina']}{d['radius']} {d['comment']}"
    ]
    buttons = [
        [CallbackButton(text="С начало", payload="beginning"),
         CallbackButton(text="Вид фасада", payload="view_facade")],
        [CallbackButton(text="еще размеры", payload="add_dimensions"),
         CallbackButton(text="завершить", payload="Complete")]
    ]
    payload = ButtonsPayload(buttons=buttons).pack()
    await event.message.answer(f"{dlina}x{shirina} добавлен", attachments=[payload])


@router.message_callback(F.callback.payload == "beginning")
async def fasad_beginning(event: MessageCallback, context: MemoryContext):
    await context.set_state(Fasad.number)
    await event.message.answer("Выберите номер фасада", attachments=[kb.in_ris_facade])
    await event.answer()


@router.message_callback(F.callback.payload == "view_facade")
async def fasad_view(event: MessageCallback, context: MemoryContext):
    await context.set_state(Fasad.risunok)
    await event.message.answer("Выберите вид фасада", attachments=[kb.in_vid_facade])
    await event.answer()


@router.message_callback(F.callback.payload == "add_dimensions")
async def fasad_add_dim(event: MessageCallback, context: MemoryContext):
    await context.set_state(Fasad.dimensions)
    await event.message.answer("Пишите размеры через пробел\nили нажмите на отмена")
    await event.answer()


@router.message_callback(F.callback.payload == "Complete")
async def fasad_complete(event: MessageCallback, context: MemoryContext):
    d = await context.get_data()
    fas_line = '\n'.join(d['fasad_line'])
    zakaz_one(fas_line, d['zakaz'])
    await event.message.answer(f"заказ {d['zakaz']} завершен")
    await context.clear()
    await event.answer()


@router.message_callback(F.callback.payload == "dir_delete")
async def delete_dir(event: MessageCallback, context: MemoryContext):
    await context.set_state(Fasad.dir_del)
    await event.message.answer("Пишите папку для удаления\nили в конце it или ss")
    await event.answer()


@router.message_created(Fasad.dir_del)
async def delete_it_ss(event: MessageCreated, context: MemoryContext):
    text = event.message.body.text
    await context.update_data(dir_del=text)
    try:
        if len(text) == 4:
            shutil.rmtree(f"{put_555it}/{text}it")
            shutil.rmtree(f"{put_555ss}/{text}h")
            await event.message.answer("удаление завершено")
            await context.clear()
            return
        if text[-2:].lower() == 'it':
            shutil.rmtree(f"{put_555it}/{text}")
            await event.message.answer(f"удаление {text} завершено")
        elif text[-2:].lower() == 'ss':
            shutil.rmtree(f"{put_555ss}/{text[:4]}h")
            await event.message.answer(f"удаление {text} завершено")
    except Exception as ex:
        await event.message.answer(f"ошибка! {ex}, проверьте папку")
    await context.clear()


@router.message_callback()
async def cmd_zaks_err(event: MessageCallback):
    await event.message.answer(f'ошибка! {event.callback.payload}')
    await event.answer()


@router.message_created()
async def text_proc(event: MessageCreated, bot: Bot):
    text = event.message.body.text
    if not text or len(text) != 6:
        return
    try:
        if text[-2:].lower() == 'ss':
            if os.path.isdir(put_555ss + "/" + text[:4] + "h"):
                shutil.make_archive(f"{put_ss}ss", 'zip', put_555ss + "/" + text[:4] + "h")
                file = InputMedia(path=f"{put_ss}ss.zip")
                attachment = await bot.upload_media(file)
                await event.message.answer(attachments=[attachment])
                await event.message.answer("копирования завершен")
                os.remove(f"{put_ss}ss.zip")
            else:
                await event.message.answer('ss stanok off или нет заказа')
        elif text[-2:].lower() == 'it':
            if os.path.isdir(put_555it + "/" + text[:4] + "it"):
                shutil.make_archive(f"{put_it}it", 'zip', put_555it + "/" + text[:4] + "it")
                file = InputMedia(path=f"{put_it}it.zip")
                attachment = await bot.upload_media(file)
                await event.message.answer(attachments=[attachment])
                await event.message.answer("копирования завершен")
                os.remove(f"{put_it}it.zip")
            else:
                await event.message.answer('it stanok off или нет заказа')
        elif text[-2:].lower() == 'nc':
            if os.path.isdir(put_555nc + "/" + text[:4] + "nc"):
                shutil.make_archive(f"{put_nc}nc", 'zip', put_555nc + "/" + text[:4] + "nc")
                file = InputMedia(path=f"{put_nc}nc.zip")
                attachment = await bot.upload_media(file)
                await event.message.answer(attachments=[attachment])
                await event.message.answer("копирования завершен")
                os.remove(f"{put_nc}nc.zip")
            else:
                await event.message.answer('nc stanok off или нет заказа')
        elif text[:2].lower() == 'ss':
            Fasad.zak_az.append(text[2:])
            await event.message.answer(f'{text[2:]} Добавлен в массив zak_az')
        else:
            await event.message.answer('ошибка!')
    except Exception:
        await event.message.answer('Удалите папку')


@router.message_created()
async def echo_send(event: MessageCreated, bot: Bot):
    text = event.message.body.text
    if not text or len(text) not in [4, 5]:
        return

    if await db.db_check(event.message.sender.user_id, "Admin"):
        try:
            ms_txt = serd_nomer(text, "Сердюченко") if len(text) == 5 else text
            btn = CallbackButton(text='⚙ ' + ms_txt + ' ⚙', payload=f'zakaz{text}')
            payload = ButtonsPayload(buttons=[[btn]]).pack()
            await event.message.answer(f"<pre>{serdyuch(ms_txt)}</pre>", attachments=[payload])
        except Exception:
            await event.message.answer('ошибка!')
    elif await db.db_check(event.message.sender.user_id, "Ser"):
        try:
            ms_txt = serd_nomer_4(text, "Сердюченко")
            await event.message.answer(f"<pre>{serdyuch(ms_txt)}</pre>")
            await bot.send_message(user_id=id_klient['bot'], text=f'Сердюченко {text} -> {ms_txt}')
        except Exception:
            await event.message.answer('ошибка!')
    elif await db.db_check(event.message.sender.user_id, "Ellion"):
        try:
            ms_txt = serd_nomer_4(text, "Эллион")
            await event.message.answer(f"<pre>{serdyuch(ms_txt)}</pre>")
            await bot.send_message(user_id=id_klient['bot'], text=f'Эллион {text} -> {ms_txt}')
        except Exception:
            await event.message.answer('ошибка!')
    elif await db.db_check(event.message.sender.user_id, "Frezer") or await db.db_check(event.message.sender.user_id,
                                                                                        "sklad"):
        try:
            ms_txt = serd_nomer(text, "Сердюченко") if len(text) == 5 else text
            await event.message.answer(f"<pre>{serdyuch(ms_txt)}</pre>")
        except Exception:
            await event.message.answer('ошибка!')
    else:
        try:
            ms_txt = text
            await event.message.answer(
                f"<pre>{order_name(ms_txt, await db.db_surname_check(event.message.sender.user_id))}</pre>")
        except Exception:
            await event.message.answer('ошибка!')


@router.message_created(F.message.body.text.startswith("##"))
async def echo_zakaz_one(event: MessageCreated):
    await event.message.answer('Добавлен в заказ', zakaz_one(event.message.body.text[2:]))


@router.message_created(F.message.body.text.startswith("$$$"))
async def echo_otchet_one(event: MessageCreated):
    await event.message.answer(f'Добавлен в заказ {event.message.body.text[3:]}',
                               net_otchot(event.message.body.text[3:]))


@router.message_created()
async def echo(event: MessageCreated):
    await event.message.answer('ошибка!')