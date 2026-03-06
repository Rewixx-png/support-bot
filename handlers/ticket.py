import html
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import ReplyTicket
from callbacks import TicketCD
from keyboards import get_ticket_kb, get_cancel_kb
from config import OWNER_ID
from database import db
from .user import get_media_type

router = Router()

@router.callback_query(TicketCD.filter(F.action == "reply"))
async def process_reply_button(call: CallbackQuery, callback_data: TicketCD, state: FSMContext, bot: Bot):
    original_html = call.message.html_text
    new_text = original_html + "\n\n✍️ <b>Напишите ответ:</b>"
    
    await bot.edit_message_text(
        text=new_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_cancel_kb(),
        parse_mode="HTML"
    )
    
    await state.set_state(ReplyTicket.waiting_for_reply)
    await state.update_data(
        ticket_id=callback_data.ticket_id,
        msg_id=call.message.message_id,
        target='user' if call.from_user.id == OWNER_ID else 'owner',
        original_html=original_html
    )
    await call.answer()

@router.message(ReplyTicket.waiting_for_reply)
async def process_reply_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ticket_id = data['ticket_id']
    msg_id = data['msg_id']
    target = data['target']
    original_html = data['original_html']
    
    ticket = await db.get_ticket(ticket_id)
    if not ticket or ticket['status'] == 'closed':
        await message.answer("⚠️ Этот тикет уже закрыт.")
        await state.clear()
        return

    media_type = get_media_type(message)
    raw_reply = message.text or message.caption or media_type
    safe_reply = html.escape(raw_reply)
    
    final_text = original_html + f"\n\n💬 <b>Ваш ответ:</b> <blockquote>{safe_reply}</blockquote>"
    
    try:
        await bot.edit_message_text(
            text=final_text,
            chat_id=message.chat.id,
            message_id=msg_id,
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    if target == 'user':
        chat_id = ticket['user_id']
        thread_id = ticket['user_topic_id']
        info_text = f"🛡 <b>Владелец ответил на ваш вопрос:</b>\n<blockquote>{safe_reply}</blockquote>"
    else:
        chat_id = OWNER_ID
        thread_id = ticket['owner_topic_id']
        safe_user_name = html.escape(message.from_user.first_name)
        info_text = (
            f"📨 <b>Новое сообщение</b>\n\n"
            f"👤 <b>Пользователь:</b> {safe_user_name}\n"
            f"📧 <b>UserName:</b> @{message.from_user.username or 'Скрыт'}\n"
            f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n\n"
            f"📝 <b>Текст:</b>\n<blockquote>{safe_reply}</blockquote>"
        )
        
    if message.text is None:
        try:
            await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                message_thread_id=thread_id
            )
        except Exception:
            pass

    sent_msg = await bot.send_message(
        chat_id=chat_id,
        message_thread_id=thread_id,
        text=info_text,
        reply_markup=get_ticket_kb(ticket_id, 0),
        parse_mode="HTML"
    )
    
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=sent_msg.message_id,
        reply_markup=get_ticket_kb(ticket_id, sent_msg.message_id)
    )
    
    await state.clear()

    try:
        await message.delete()
    except Exception:
        pass

@router.callback_query(TicketCD.filter(F.action == "close"))
async def process_close_ticket(call: CallbackQuery, callback_data: TicketCD, bot: Bot):
    ticket_id = callback_data.ticket_id
    ticket = await db.get_ticket(ticket_id)
    
    if not ticket or ticket['status'] == 'closed':
        await call.answer("Тикет уже закрыт", show_alert=True)
        return

    await db.close_ticket(ticket_id)
    
    try:
        await bot.close_forum_topic(chat_id=ticket['user_id'], message_thread_id=ticket['user_topic_id'])
        await bot.delete_forum_topic(chat_id=ticket['user_id'], message_thread_id=ticket['user_topic_id'])
    except Exception:
        pass

    try:
        await bot.close_forum_topic(chat_id=OWNER_ID, message_thread_id=ticket['owner_topic_id'])
        await bot.delete_forum_topic(chat_id=OWNER_ID, message_thread_id=ticket['owner_topic_id'])
    except Exception:
        pass

    try:
        await call.message.edit_text(call.message.html_text + "\n\n🚫 <b>[Тикет закрыт]</b>", parse_mode="HTML")
    except Exception:
        pass

    await call.answer("Тикет закрыт и удален!")