from aiogram.filters.callback_data import CallbackData

class TicketCD(CallbackData, prefix="ticket"):
    action: str
    ticket_id: int
    msg_id: int