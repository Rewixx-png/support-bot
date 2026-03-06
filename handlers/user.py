import html
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import CreateTopic
from keyboards import get_start_kb, get_cancel_kb, get_ticket_kb
from config import OWNER_ID
from database import db

router = Router()

def get_media_type(message: Message) -> str:
    if message.photo: return "🖼 Фото"
    if message.video: return "🎥 Видео"
    if message.voice: return "🎤 Голосовое сообщение"
    if message.video_note: return "⏺ Кружочек"
    if message.document: return "📄 Документ"
    if message.audio: return "🎵 Аудио"
    if message.sticker: return "✨ Стикер"
    if message.animation: return "🎞 GIF"
    return "📎 Медиафайл"

@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    try:
        await bot.edit_general_forum_topic(chat_id=message.chat.id, name="Главное меню")
    except Exception:
        pass
    
    text = (
        "👋 <b>Добро пожаловать в службу поддержки!</b>\n\n"
        "Здесь вы можете создать тикет, и мы ответим вам в кратчайшие сроки.\n"
        "Бот поддерживает отправку текста, фото, видео, голосовых и других файлов.\n\n"
        "Нажмите кнопку ниже, чтобы начать."
    )
    await message.answer(text, reply_markup=get_start_kb(), parse_mode="HTML")

@router.callback_query(F.data == "cancel_action")
async def process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.delete()
    except Exception:
        await call.message.edit_text("🚫 Действие отменено.")
    await call.answer("Отменено")

@router.callback_query(F.data == "start_create_topic")
async def process_create_topic(call: CallbackQuery, state: FSMContext):
    msg = await call.message.edit_text("✍️ <b>Напишите название темы обращения:</b>", reply_markup=get_cancel_kb(), parse_mode="HTML")
    await state.update_data(prompt_msg_id=msg.message_id)
    await state.set_state(CreateTopic.name)

@router.message(CreateTopic.name)
async def process_topic_name(message: Message, state: FSMContext, bot: Bot):
    if message.text and message.text.startswith('/'):
        await message.answer("⚠️ Пожалуйста, введите название темы обычным текстом:", reply_markup=get_cancel_kb())
        return

    data = await state.get_data()
    old_prompt_id = data.get('prompt_msg_id')
    if old_prompt_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=old_prompt_id)
            await message.delete()
        except Exception:
            pass

    topic_name = message.text or "Новая тема"
    
    try:
        forum_topic = await bot.create_forum_topic(chat_id=message.chat.id, name=topic_name)
    except Exception as e:
        if "the chat is not a forum" in str(e):
            error_text = (
                "⚠️ <b>Включите поддержку топиков в Mini App!</b>\n\n"
                "1. Зайдите в @BotFather.\n"
                "2. Нажмите на кнопку <b>[ ] Open</b> (или <b>Edit Bots</b>) слева внизу.\n"
                "3. В окне выберите вашего бота.\n"
                "4. Перейдите в <b>Bot Settings</b>.\n"
                "5. Включите <b>Threaded Mode</b>.\n"
                "6. Закройте окно и напишите /start"
            )
            await message.answer(error_text, parse_mode="HTML")
        else:
            await message.answer(f"❌ Ошибка создания топика: {e}")
        return

    text_prompt = (
        "📨 <b>Отлично! Топик создан.</b>\n\n"
        "Теперь отправьте ваше сообщение (поддерживаются текст, фото, видео, голосовые и т.д.). "
        "Оно будет передано владельцу."
    )
    prompt_msg = await bot.send_message(
        chat_id=message.chat.id,
        message_thread_id=forum_topic.message_thread_id,
        text=text_prompt,
        reply_markup=get_cancel_kb(),
        parse_mode="HTML"
    )
    
    await state.update_data(
        topic_name=topic_name, 
        user_topic_id=forum_topic.message_thread_id,
        prompt_msg_id=prompt_msg.message_id
    )
    await state.set_state(CreateTopic.first_message)

@router.message(CreateTopic.first_message)
async def process_first_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_topic_id = data['user_topic_id']
    topic_name = data['topic_name']
    prompt_msg_id = data.get('prompt_msg_id')

    try:
        if prompt_msg_id:
            await bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
    except Exception:
        pass

    try:
        owner_topic = await bot.create_forum_topic(
            chat_id=OWNER_ID, 
            name=f"{topic_name} ({message.from_user.first_name})"
        )
        owner_topic_id = owner_topic.message_thread_id
    except Exception as e:
        if "the chat is not a forum" in str(e):
            await message.answer("❌ Ошибка: У владельца не включен Threaded Mode в @BotFather (Mini App).")
        else:
            await message.answer(f"❌ Ошибка при создании топика у владельца: {e}")
        return

    ticket_id = await db.create_ticket(message.from_user.id, user_topic_id, owner_topic_id)

    user_name = html.escape(message.from_user.first_name)
    username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"
    user_id = message.from_user.id
    
    media_type = get_media_type(message)
    raw_text = message.text or message.caption or media_type
    safe_text = html.escape(raw_text)

    info_text = (
        f"🔔 <b>Новое обращение</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_name}\n"
        f"📧 <b>UserName:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"📝 <b>Текст:</b>\n<blockquote>{safe_text}</blockquote>"
    )

    if message.text is None:
        try:
            await bot.copy_message(
                chat_id=OWNER_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                message_thread_id=owner_topic_id
            )
        except Exception:
            pass
    
    sent_msg = await bot.send_message(
        chat_id=OWNER_ID,
        message_thread_id=owner_topic_id,
        text=info_text,
        reply_markup=get_ticket_kb(ticket_id, 0),
        parse_mode="HTML"
    )

    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID,
        message_id=sent_msg.message_id,
        reply_markup=get_ticket_kb(ticket_id, sent_msg.message_id)
    )

    await bot.send_message(
        chat_id=message.chat.id,
        message_thread_id=user_topic_id,
        text=f"✅ <b>Ваше сообщение:</b>\n<blockquote>{safe_text}</blockquote>\n\nУспешно отправлено владельцу! Ожидайте ответа.",
        parse_mode="HTML"
    )
    
    await state.clear()
    
    try:
        await message.delete()
    except Exception:
        pass