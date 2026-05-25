from aiogram.fsm.state import State, StatesGroup


class AddProductState(StatesGroup):
    start_adding = State()
    add_attribute = State()
    confirm_adding = State()

class EditProductState(StatesGroup):
    edit_field = State()