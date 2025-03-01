from aiogram.fsm.state import StatesGroup, State

class User(StatesGroup):
    current_mode = State()

user = User()