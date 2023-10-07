from aiogram.fsm.state import StatesGroup, State


class AdminSupportStates(StatesGroup):
    utm = State()
    Spam_Input = State()
    link_get_priz = State()
    priz = State()
    channel = State()
    admins_list = State()
    info = State()
