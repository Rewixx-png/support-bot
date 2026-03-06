from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks import TicketCD

def get_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📝 Создать тему", callback_data="start_create_topic", style="success")]
    ])

def get_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action", style="danger")]
    ])

def get_ticket_kb(ticket_id: int, msg_id: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💬 Ответить", callback_data=TicketCD(action="reply", ticket_id=ticket_id, msg_id=msg_id).pack(), style="primary")],[InlineKeyboardButton(text="🔒 Закрыть тикет", callback_data=TicketCD(action="close", ticket_id=ticket_id, msg_id=msg_id).pack(), style="danger")]
    ])