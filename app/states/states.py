from aiogram.fsm.state import State, StatesGroup


class AddProductState(StatesGroup):
    name = State()
    price = State()
    priority = State()

class EditProductState(StatesGroup):
    choose_field = State()
    edit_field = State()
    confirm_edit = State()
