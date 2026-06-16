from maxapi.types.attachments.buttons import (
    MessageButton,
    CallbackButton,
    ClipboardButton,
    LinkButton,
)
from maxapi.types.attachments.attachment import ButtonsPayload
from time import strftime
import os

# ----------------------------------------------------------------------
# Вспомогательные переменные (год, месяц и т.д.)
# ----------------------------------------------------------------------
month, month_1 = strftime('%y'), str(int(strftime('%y')) - 1)
year, year_1, year_2 = strftime('%Y'), str(int(strftime('%Y')) - 1), str(int(strftime('%Y')) - 2)
year_3, year_4, year_5 = str(int(strftime('%Y')) - 3), str(int(strftime('%Y')) - 4), str(int(strftime('%Y')) - 5)

# ----------------------------------------------------------------------
# Базовые reply‑кнопки (MessageButton)
# ----------------------------------------------------------------------
pochta = MessageButton(text='📨 Почта', payload='📨 Почта')
otchet = MessageButton(text="📝 Отчет", payload="📝 Отчет")
dolgi = MessageButton(text='📕 Долги', payload='📕 Долги')
serdyuch = MessageButton(text='🚻 Сердюченко', payload='🚻 Сердюченко')
forma_fasad = MessageButton(text='🚪 Фасады', payload='🚪 Фасады')
zarplata = MessageButton(text='💰 Зарплата', payload='💰 Зарплата')
klient = MessageButton(text='👨‍💼 Клиенты', payload='👨‍💼 Клиенты')
info_zakaza = MessageButton(text='❗Инфо по заказу', payload='❗Инфо по заказу')
obnovit = MessageButton(text=f"🔄 Обновить", payload=f"🔄 Обновить")
kursi_valyut = MessageButton(text='💵 Курсы валют', payload='💵 Курсы валют')
zametki = MessageButton(text='📝Заметки', payload='📝Заметки')
raskroy = MessageButton(text='🪚 Раскрой', payload='🪚 Раскрой')
frezer = MessageButton(text='🕹 Фрезер', payload='🕹 Фрезер')
press = MessageButton(text='⚙️ Пресс', payload='⚙️ Пресс')
price = MessageButton(text='💷 Стоимость', payload='💷 Стоимость')
plenka = MessageButton(text='🟧 Пленки', payload='🟧 Пленки')
st_plenka = MessageButton(text='📊 Статистика', payload='📊 Статистика')
raskroy_ostatok = MessageButton(text='🪚 Раскрой/ост.', payload='🪚 Раскрой/ост.')
raskroy_zarplata = MessageButton(text='🪚 Раскрой/зар.', payload='🪚 Раскрой/зар.')
client_all = MessageButton(text='⚙️ Мои заказы', payload='⚙️ Мои заказы')
client_credit = MessageButton(text='⚙️ Мои долги', payload='⚙️ Мои долги')

# ----------------------------------------------------------------------
# Reply‑клавиатуры (списки списков MessageButton)
# ----------------------------------------------------------------------
bot_kb = [
    [MessageButton(text=f"Обновить {year}", payload=f"Обновить {year}"),
     MessageButton(text=f"Обновить {year_1}", payload=f"Обновить {year_1}"),
     MessageButton(text='Доп. кнопки', payload='Доп. кнопки')],
    [zametki, MessageButton(text='Срочность', payload='Срочность'), MessageButton(text='Заказы', payload='Заказы')],
    [dolgi, pochta, otchet],
    [klient, serdyuch, zarplata],
    [raskroy, frezer, press],
    [forma_fasad, plenka, price],
    [st_plenka, info_zakaza, raskroy_ostatok]
]

vova_kb = [
    [obnovit, pochta, otchet],
    [klient, dolgi, zarplata],
    [raskroy, frezer, press],
    [st_plenka, info_zakaza, raskroy_ostatok],
    [forma_fasad, plenka, price],
    [raskroy_zarplata],
]

serdyuch_kb = [
    [MessageButton(text=f"Обновить {year}", payload=f"Обновить {year}"),
     MessageButton(text=f"Обновить {year_1}", payload=f"Обновить {year_1}")],
    [forma_fasad, plenka, price]
]

shef_kb = [
    [obnovit, pochta, otchet],
    [klient, dolgi, zarplata],
    [serdyuch, info_zakaza, st_plenka],
    [raskroy, frezer, press],
    [forma_fasad, plenka, price],
]

all_user = [[forma_fasad, plenka, price]]
client_kb = [[forma_fasad, plenka, price], [client_all, client_credit]]
ellion_kb = [[forma_fasad, plenka, price]]

admin_kb = [
    [MessageButton(text='Объявление', payload='Объявление'),
     MessageButton(text='Картинка', payload='Картинка'),
     MessageButton(text='Аккаунты', payload='Аккаунты')],
    [MessageButton(text='Добавить', payload='Добавить'),
     MessageButton(text='Обновить', payload='Обновить'),
     MessageButton(text='Удалить', payload='Удалить')],
    [MessageButton(text='Рестарт ПК', payload='Рестарт ПК'),
     MessageButton(text='✖ Отмена', payload='✖ Отмена'),
     MessageButton(text='🔄 Рестарт', payload='🔄 Рестарт')],
    [MessageButton(text='🔙 Назад', payload='🔙 Назад'),
     MessageButton(text='Переписать', payload='Переписать'),
     MessageButton(text='Акции', payload='Акции')]
]

frezer_kb = [
    [forma_fasad, price, frezer],
    [MessageButton(text='ss_станок', payload='ss_станок'),
     MessageButton(text='nc_станок', payload='nc_станок'),
     MessageButton(text='it_станок', payload='it_станок')],
    [MessageButton(text='✖ Отмена', payload='✖ Отмена'),
     MessageButton(text='Архив', payload='Архив'),
     MessageButton(text='+132 фреза', payload='+132 фреза')]
]

frezer_nc = [
    [MessageButton(text='Подклад', payload='Подклад'),
     MessageButton(text='Подача', payload='Подача')],
    [MessageButton(text='↩️ Назад', payload='↩️ Назад'),
     MessageButton(text='✖ Отмена', payload='✖ Отмена')]
]

frezer_it = [
    [MessageButton(text='№ фрезы', payload='№ фрезы'),
     MessageButton(text='Толщина МДФ', payload='Толщина МДФ')],
    [MessageButton(text='↩️ Назад', payload='↩️ Назад'),
     MessageButton(text='✖ Отмена', payload='✖ Отмена')]
]

# ----------------------------------------------------------------------
# Упаковка reply‑клавиатур в ButtonsPayload
# ----------------------------------------------------------------------
kb_bot = ButtonsPayload(buttons=bot_kb).pack()
kb_vova = ButtonsPayload(buttons=vova_kb).pack()
kb_serdyuch = ButtonsPayload(buttons=serdyuch_kb).pack()
kb_shef = ButtonsPayload(buttons=shef_kb).pack()
kb_all_user = ButtonsPayload(buttons=all_user).pack()
kb_admin = ButtonsPayload(buttons=admin_kb).pack()
kb_frezer = ButtonsPayload(buttons=frezer_kb).pack()
kb_frezer_nc = ButtonsPayload(buttons=frezer_nc).pack()
kb_frezer_it = ButtonsPayload(buttons=frezer_it).pack()
kb_clent = ButtonsPayload(buttons=client_kb).pack()
kb_ellion = ButtonsPayload(buttons=ellion_kb).pack()

# ----------------------------------------------------------------------
# Inline‑клавиатуры (CallbackButton)
# ----------------------------------------------------------------------
kb_in = [
    [CallbackButton(text='156', payload='value_156'),
     CallbackButton(text='144_1', payload='value_144_1'),
     CallbackButton(text='144_2', payload='value_144_2'),
     CallbackButton(text='144_3', payload='value_144_3')],
    [CallbackButton(text='под 45', payload='value_45'),
     CallbackButton(text='136_1', payload='value_136_1'),
     CallbackButton(text='136_2', payload='value_136_2'),
     CallbackButton(text='136_3', payload='value_136_3')],
    [CallbackButton(text='Без хдф', payload='value_bez_xdf'),
     CallbackButton(text='RY=44.5', payload='value_ramy_45'),
     CallbackButton(text='под 92', payload='value_92')]
]

dop_knopki = [
    [CallbackButton(text="Del", payload="del_value"),
     CallbackButton(text="Copy_it", payload="copyit_value_it"),
     CallbackButton(text="Copy_ss", payload="copyss_value_ss"),
     CallbackButton(text="Copy_nc", payload="copync_value_nc")],
    [CallbackButton(text="Папки", payload="papki_value"),
     CallbackButton(text="Copy", payload="copy_value"),
     CallbackButton(text="zk_Del", payload="zk_Del_value"),
     CallbackButton(text="Temp", payload="temp_value")],
    [CallbackButton(text="Файл", payload="fail_value"),
     CallbackButton(text="Скрин", payload="skrin_value"),
     CallbackButton(text="Процесс", payload="proc_value"),
     CallbackButton(text="Отметка", payload="otmetka_value")],
    [CallbackButton(text="Процесс + Отметка", payload="proc_otmetka_value"),
     CallbackButton(text='Удалить', payload="dir_delete"),
     CallbackButton(text='Фасад', payload="do_facade")],
]

change_order = [
    [CallbackButton(text='Заказ №', payload="zakaz_value"),
     CallbackButton(text='Добавить', payload="change_value")],
]

static_plenka = [
    [CallbackButton(text="По номеру пленки", payload="static_plenki")],
    [CallbackButton(text="По форме фасада", payload="static_fasad")],
    [CallbackButton(text="По толщине МДФ", payload="static_mdf")]
]

actions = [
    [CallbackButton(text="Просмотр", payload="view_actions")],
    [CallbackButton(text="Редоктировать", payload="view_add_actions")],
    [CallbackButton(text="Финансы", payload="view_add_finance")],
]

vid_facade = [
    [CallbackButton(text="Фасад", payload="Фасад_Ris"),
     CallbackButton(text="СТЕКЛО", payload="СТЕКЛО_Ris"),
     CallbackButton(text="ПСЯ", payload="ПСЯ_Ris")],
    [CallbackButton(text="Бутыл.", payload="Бутыл._Ris"),
     CallbackButton(text="Планка", payload="Планка_Ris"),
     CallbackButton(text="ПЕРЕПЛЕТ", payload="ПЕРЕПЛЕТ_Ris")],
]

# Упаковка inline‑клавиатур
in_kn = ButtonsPayload(buttons=kb_in).pack()
dop_kn = ButtonsPayload(buttons=dop_knopki).pack()
in_change_order = ButtonsPayload(buttons=change_order).pack()
in_static_plenka = ButtonsPayload(buttons=static_plenka).pack()
in_actions = ButtonsPayload(buttons=actions).pack()
in_vid_facade = ButtonsPayload(buttons=vid_facade).pack()

# ----------------------------------------------------------------------
# Динамические inline‑клавиатуры (функция-помощник)
# ----------------------------------------------------------------------
number_fasad = [str(j) for j in sorted([int(i) for i in os.listdir('images')])]

mesyac = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
letter = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
          'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ы', 'Э', 'Ю', 'Я']
group = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

dolgi_year = [year, year_1, year_2]
client_year = [year, year_1, year_2, year_3, year_4, year_5]

def vivod_inlinekey(lst, number, call_txt):
    result = []
    for i in range(0, len(lst), number):
        row = []
        for j in lst[i:i+number]:
            row.append(CallbackButton(text=j, payload=f'{call_txt}{j}'))
        result.append(row)
    return result

# Упаковка динамических клавиатур
in_risunok = ButtonsPayload(buttons=vivod_inlinekey(number_fasad, 7, '$')).pack()
in_ris_facade = ButtonsPayload(buttons=vivod_inlinekey(number_fasad, 7, 'facade')).pack()
in_mesyac = ButtonsPayload(buttons=vivod_inlinekey(mesyac, 4, '!!!')).pack()
in_letter = ButtonsPayload(buttons=vivod_inlinekey(letter, 8, '%%%')).pack()
in_ris_price = ButtonsPayload(buttons=vivod_inlinekey(number_fasad, 7, 'fasad')).pack()
in_group_pl = ButtonsPayload(buttons=vivod_inlinekey(group, 6, 'group')).pack()
in_group_sort = ButtonsPayload(buttons=vivod_inlinekey(group, 6, 'sort')).pack()
in_dolgi_year = ButtonsPayload(buttons=vivod_inlinekey(client_year, 3, 'year')).pack()
in_my_dolgi_year = ButtonsPayload(buttons=vivod_inlinekey(client_year, 3, 'my_year')).pack()
in_zarplata_year = ButtonsPayload(buttons=vivod_inlinekey(dolgi_year, 3, 'zar_year')).pack()

# ----------------------------------------------------------------------
# Экспортируемые имена (для удобства импорта)
# ----------------------------------------------------------------------
__all__ = [
    'kb_bot', 'kb_vova', 'kb_serdyuch', 'kb_shef', 'kb_all_user', 'kb_admin',
    'kb_frezer', 'kb_frezer_nc', 'kb_frezer_it', 'kb_clent', 'kb_ellion',
    'in_kn', 'dop_kn', 'in_change_order', 'in_static_plenka', 'in_actions', 'in_vid_facade',
    'in_risunok', 'in_ris_facade', 'in_mesyac', 'in_letter', 'in_ris_price',
    'in_group_pl', 'in_group_sort', 'in_dolgi_year', 'in_my_dolgi_year', 'in_zarplata_year',
    'pochta', 'otchet', 'dolgi', 'serdyuch', 'forma_fasad', 'zarplata', 'klient',
    'info_zakaza', 'obnovit', 'kursi_valyut', 'zametki', 'raskroy', 'frezer',
    'press', 'price', 'plenka', 'st_plenka', 'raskroy_ostatok', 'raskroy_zarplata',
    'client_all', 'client_credit'
]