import html
from maxapi import Router, Bot, F
from maxapi.types import MessageCreated, MessageCallback
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.types.attachments.attachment import ButtonsPayload
import app.database as db
import app.keyboards_notes as kb
from app.keyboards import kb_bot

router_notes = Router()


class Notes(StatesGroup):
    fsm_note_name = State()
    fsm_note_text = State()
    note_number = State()
    note_list = State()
    note_all = State()
    note_delete = State()
    note_edit = State()
    name_text = State()
    note_new_add = State()
    new_text = State()
    add_text = State()


# Словарь эмодзи для типов заметок
type_dict = {
    'text': '📝',
    'photo': '🖼️',
    'document': '📄',
    'voice': '🎤',
    'audio': '🎵',
    'video': '📽️',
    'video_note': '🎦'
}


# --- Функция для преобразования форматирования Telegram в HTML ---
def get_html_text(text: str, entities: list = None) -> str:
    if not entities:
        return html.escape(text)

    # Сортируем сущности, чтобы обрабатывать их последовательно
    sorted_entities = sorted(entities, key=lambda e: e.offset)
    result = ""
    last_offset = 0

    for entity in sorted_entities:
        # Добавляем текст до текущей сущности
        result += html.escape(text[last_offset:entity.offset])

        # Получаем текст сущности
        entity_text = text[entity.offset:entity.offset + entity.length]
        entity_text_quoted = html.escape(entity_text)

        # Оборачиваем в HTML теги в зависимости от типа
        if entity.type == 'bold':
            result += f"<b>{entity_text_quoted}</b>"
        elif entity.type == 'italic':
            result += f"<i>{entity_text_quoted}</i>"
        elif entity.type == 'underline':
            result += f"<u>{entity_text_quoted}</u>"
        elif entity.type == 'strikethrough':
            result += f"<s>{entity_text_quoted}</s>"
        elif entity.type == 'code':
            result += f"<code>{entity_text_quoted}</code>"
        elif entity.type == 'pre':
            result += f"<pre>{entity_text_quoted}</pre>"
        elif entity.type == 'blockquote':
            result += f"<blockquote>{entity_text_quoted}</blockquote>"
        elif entity.type == 'text_link':
            url = entity.url
            result += f"<a href='{url}'>{entity_text_quoted}</a>"
        else:
            result += entity_text_quoted

        last_offset = entity.offset + entity.length

    # Добавляем оставшийся текст
    result += html.escape(text[last_offset:])
    return result


@router_notes.message_created(F.message.body.text == '📝Заметки')
async def note_text(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await event.message.answer("Это меню заметок", attachments=[kb.note_list])


@router_notes.message_created(F.message.body.text == '📝Добавить заметку')
async def note_text_name(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(Notes.fsm_note_name)
    await event.message.answer("Пишите название заметки 👇", attachments=[kb.note_list])


@router_notes.message_created(Notes.fsm_note_name)
async def text_note(event: MessageCreated, context: MemoryContext):
    # Название сохраняем как есть
    await context.update_data(fsm_note_name=event.message.body.text)
    await context.set_state(Notes.fsm_note_text)
    await event.message.answer(
        "Теперь отправьте содержимое заметки:\n\n"
        "📝 Текст - для текстовой заметки\n"
        "📷 Фото - для фото заметки\n"
        "🎤 Аудио/голосовое - для аудио заметки\n"
        "🎬 Видео - для видео заметки 👇",
        attachments=[kb.note_list]
    )


@router_notes.message_created(Notes.fsm_note_text)
async def save_note(event: MessageCreated, context: MemoryContext):
    file_id, note_type = None, None
    caption_text = '----'

    # Проверка типов сообщений в maxapi может отличаться, используем hasattr для безопасности
    if hasattr(event.message, 'photo') and event.message.photo:
        file_id = event.message.photo[-1].file_id
        note_type = 'photo'
        if hasattr(event.message, 'caption') and event.message.caption:
            caption_text = get_html_text(event.message.caption, getattr(event.message, 'caption_entities', None))
    elif hasattr(event.message, 'document') and event.message.document:
        file_id = event.message.document.file_id
        note_type = 'document'
        if hasattr(event.message, 'caption') and event.message.caption:
            caption_text = get_html_text(event.message.caption, getattr(event.message, 'caption_entities', None))
    elif hasattr(event.message, 'voice') and event.message.voice:
        file_id = event.message.voice.file_id
        note_type = 'voice'
    elif hasattr(event.message, 'audio') and event.message.audio:
        file_id = event.message.audio.file_id
        note_type = 'audio'
    elif hasattr(event.message, 'video') and event.message.video:
        file_id = event.message.video.file_id
        note_type = 'video'
    elif hasattr(event.message, 'video_note') and event.message.video_note:
        file_id = event.message.video_note.file_id
        note_type = 'video_note'
    else:
        # Текстовое сообщение
        note_type = 'text'
        caption_text = get_html_text(event.message.body.text, getattr(event.message.body, 'entities', None))

    await context.update_data(fsm_note_text=caption_text)
    data_state = await context.get_data()

    await db.add_note(
        event.message.sender.user_id,
        data_state['fsm_note_name'],
        data_state['fsm_note_text'],
        note_type=note_type,
        file_id=file_id
    )
    await event.message.answer("Заметка сохранена", attachments=[kb.note_list])
    await context.clear()


@router_notes.message_created(F.message.body.text == '📋Мои заметки')
async def my_note_text(event: MessageCreated, context: MemoryContext):
    await context.clear()
    notes_dict = await db.select_note(event.message.sender.user_id)
    if notes_dict:
        await context.update_data(note_list=notes_dict)
        in_kb = []
        for key in notes_dict:
            in_kb.append([CallbackButton(
                text=f'{type_dict[notes_dict[key][2]]}{notes_dict[key][0]}',
                payload=f'notes_{key}'
            )])
        payload = ButtonsPayload(buttons=in_kb).pack()
        await event.message.answer("Ваши заметки", attachments=[payload])
    else:
        await event.message.answer("У вас нет заметок", attachments=[kb.note_list])


@router_notes.message_callback(F.callback.payload.startswith('notes_'))
async def note_view(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_namber=event.callback.payload.split('_')[1])
    await context.set_state(Notes.note_all)
    data_state = await context.get_data()
    num = int(data_state['note_namber'])
    note_data = data_state['note_list'][num]

    note_type = note_data[2]
    file_id = note_data[3]
    caption = note_data[1]

    try:
        if note_type == 'photo':
            await event.message.answer_photo(
                photo=file_id,
                caption=caption,
                attachments=[kb.edit_note]
            )
        elif note_type == 'document':
            await event.message.answer_document(
                document=file_id,
                caption=caption,
                attachments=[kb.edit_note]
            )
        elif note_type == 'voice':
            await event.message.answer_voice(
                voice=file_id,
                caption=caption,
                attachments=[kb.edit_note]
            )
        elif note_type == 'audio':
            await event.message.answer_audio(
                audio=file_id,
                caption=caption,
                attachments=[kb.edit_note]
            )
        elif note_type == 'video':
            await event.message.answer_video(
                video=file_id,
                caption=caption,
                attachments=[kb.edit_note]
            )
        elif note_type == 'video_note':
            # Видео-кружочки не поддерживают caption
            await event.message.answer_video_note(
                video_note=file_id,
                attachments=[kb.edit_note]
            )
        elif note_type == 'text':
            await event.message.answer(
                text=caption,
                attachments=[kb.edit_note]
            )
        else:
            await event.message.answer(
                text=f"⚠️ Неизвестный тип заметки: {note_type}\nСодержимое: {caption}",
                attachments=[kb.edit_note]
            )
    except Exception as e:
        await event.message.answer(
            text=f"⚠️ Ошибка доступа к файлу!\n\nНазвание: {note_data[0]}\nТекст: {caption}",
            attachments=[kb.edit_note]
        )
        print(f"Error sending note: {e}")

    await event.answer()


@router_notes.message_callback(Notes.note_all, F.callback.payload == 'note_edit')
async def edit_note(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_all=event.callback.payload)
    await context.set_state(Notes.note_edit)
    await event.message.answer("Имя заметки или текст заметки?", attachments=[kb.note_edit])
    await event.answer()


@router_notes.message_callback(Notes.note_edit, F.callback.payload == 'edit_name')
async def edit_note_name(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_edit=event.callback.payload)
    await context.set_state(Notes.name_text)
    await event.message.answer("Пишите Имя заметки 👇", attachments=[kb.note_list])
    await event.answer()


@router_notes.message_created(Notes.name_text)
async def save_note_name(event: MessageCreated, context: MemoryContext):
    await context.update_data(name_text=event.message.body.text)
    data_state = await context.get_data()
    num = int(data_state['note_namber'])
    note_name = data_state['note_list'][num][0]
    note_text = data_state['note_list'][num][1]
    await db.update_note_name(event.message.sender.user_id, data_state['name_text'], note_name, note_text)
    await event.message.answer("Имя заметки сохранено", attachments=[kb.note_list])
    await context.clear()


@router_notes.message_callback(Notes.note_edit, F.callback.payload == 'edit_text')
async def edit_note_text(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_edit=event.callback.payload)
    await context.set_state(Notes.note_new_add)
    await event.message.answer("Добавить к тексту или новый текст?", attachments=[kb.note_edit_content])
    await event.answer()


@router_notes.message_callback(Notes.note_new_add, F.callback.payload == 'new_text')
async def note_new(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_edit_text=event.callback.payload)
    await context.set_state(Notes.new_text)
    await event.message.answer("Пишите новый текст заметки 👇", attachments=[kb.note_list])
    await event.answer()


@router_notes.message_created(Notes.new_text)
async def note_new_text(event: MessageCreated, context: MemoryContext):
    # Сохраняем форматирование при редактировании
    html_text = get_html_text(event.message.body.text, getattr(event.message.body, 'entities', None))
    await context.update_data(new_text=html_text)
    data_state = await context.get_data()
    num = int(data_state['note_namber'])
    note_name = data_state['note_list'][num][0]
    note_text = data_state['note_list'][num][1]
    await db.update_note_text(event.message.sender.user_id, data_state['new_text'], note_name, note_text)
    await event.message.answer("Новый текст сохранён", attachments=[kb.note_list])
    await context.clear()


@router_notes.message_callback(Notes.note_new_add, F.callback.payload == 'add_text')
async def note_add(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_edit_text=event.callback.payload)
    await context.set_state(Notes.add_text)
    await event.message.answer("Пишите текст для добавления к заметке 👇", attachments=[kb.note_list])
    await event.answer()


@router_notes.message_created(Notes.add_text)
async def note_add_text(event: MessageCreated, context: MemoryContext):
    # Сохраняем форматирование при добавлении
    html_text = get_html_text(event.message.body.text, getattr(event.message.body, 'entities', None))
    await context.update_data(add_text=html_text)
    data_state = await context.get_data()
    num = int(data_state['note_namber'])
    note_name = data_state['note_list'][num][0]
    note_text = data_state['note_list'][num][1]

    if note_text == '----':
        all_text = f"{data_state['add_text']}"
    else:
        all_text = f"{note_text}\n----\n{data_state['add_text']}"

    await db.update_note_text(event.message.sender.user_id, all_text, note_name, note_text)
    await event.message.answer("Текст добавлен к заметке", attachments=[kb.note_list])
    await context.clear()


@router_notes.message_callback(Notes.note_all, F.callback.payload == 'note_delete')
async def delete_note(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_all=event.callback.payload)
    await context.set_state(Notes.note_delete)
    data_state = await context.get_data()
    num = int(data_state['note_namber'])
    await event.message.answer(
        f"{type_dict[data_state['note_list'][num][2]]}{data_state['note_list'][num][0]}",
        attachments=[kb.note_delete]
    )
    await event.answer()


@router_notes.message_callback(Notes.note_delete, F.callback.payload == 'delete_note')
async def delete_note_es(event: MessageCallback, context: MemoryContext):
    await context.update_data(note_delete=event.callback.payload)
    data_state = await context.get_data()
    num = int(data_state['note_namber'])
    await db.note_delete(
        event.callback.user.user_id,
        data_state['note_list'][num][0],
        data_state['note_list'][num][1]
    )
    await event.message.answer("Заметка удалена!!!", attachments=[kb.note_list])
    await event.answer()
    await context.clear()


@router_notes.message_callback(F.callback.payload == 'cancel')
async def cancel(event: MessageCallback, context: MemoryContext):
    await event.message.answer("Действие отменено", attachments=[kb.add_user_data])
    await context.clear()
    await event.answer()


@router_notes.message_callback(F.callback.payload == 'cancel_note')
async def cancel_note(event: MessageCallback, context: MemoryContext):
    await event.message.answer("Действие отменено", attachments=[kb.note_list])
    await context.clear()
    await event.answer()


@router_notes.message_created(F.message.body.text == '🏠Главное меню')
async def start_note_menu(event: MessageCreated, context: MemoryContext):
    await event.message.answer('Главное меню', attachments=[kb_bot])
    await context.clear()
