from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class User(StatesGroup):
    current_mode = State()


user = User()
