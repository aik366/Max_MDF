from maxapi.types.attachments.attachment import ButtonsPayload
from maxapi.types.attachments.buttons import (
    CallbackButton,
    MessageButton,
)

# ==========================================
# Inline-клавиатуры (для редактирования/удаления)
# ==========================================

# Подтверждение действия (редактировать или удалить)
edit_note = ButtonsPayload(buttons=[
    [CallbackButton(text='✏️Редактировать', payload='note_edit'),
     CallbackButton(text='🗑️Удалить', payload='note_delete')]
]).pack()

# Подтверждение удаления (общее)
delete = ButtonsPayload(buttons=[
    [CallbackButton(text='🗑️Удалить', payload='delete'),
     CallbackButton(text='❌Отмена', payload='cancel')]
]).pack()

# Подтверждение удаления заметки
note_delete = ButtonsPayload(buttons=[
    [CallbackButton(text='🗑️Удалить', payload='delete_note'),
     CallbackButton(text='❌Отмена', payload='cancel_note')]
]).pack()

# Выбор что редактировать в заметке (Имя или Текст)
note_edit = ButtonsPayload(buttons=[
    [CallbackButton(text='Имя заметки', payload='edit_name'),
     CallbackButton(text='Текст заметки', payload='edit_text')]
]).pack()

# Выбор режима редактирования текста (Добавить или Новый)
note_edit_content = ButtonsPayload(buttons=[
    [CallbackButton(text='Добавить', payload='add_text'),
     CallbackButton(text='Новый', payload='new_text')]
]).pack()

# Кнопка отмены
cancel_one = ButtonsPayload(buttons=[
    [CallbackButton(text='❌Отмена', payload='cancel')]
]).pack()

# ==========================================
# Reply-клавиатура (меню внутри раздела Заметки)
# ==========================================
# Используется MessageButton, так как эти кнопки отправляют текст обратно боту
note_list = ButtonsPayload(buttons=[
    [MessageButton(text="📝Добавить заметку"), MessageButton(text="📋Мои заметки")],
    [MessageButton(text="🏠Главное меню"), MessageButton(text="❌Отмена")]
]).pack()
