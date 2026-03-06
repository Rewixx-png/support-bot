from aiogram.fsm.state import StatesGroup, State

class CreateTopic(StatesGroup):
    name = State()
    first_message = State()

class ReplyTicket(StatesGroup):
    waiting_for_reply = State()