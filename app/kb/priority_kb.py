from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from app.dao.enums import Priority, ProductAppend
from app.kb import buttons


def enter_priority_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text=Priority.LOW.value, callback_data=Priority.LOW.value),
        InlineKeyboardButton(
            text=Priority.MEDIUM.value, callback_data=Priority.MEDIUM.value),
        InlineKeyboardButton(
            text=Priority.HIGH.value, callback_data=Priority.HIGH.value),
    )
    kb.row(
        InlineKeyboardButton(
            text=buttons.BUTTON_CANCEL,
            callback_data=ProductAppend.CANCEL.value)
        )
    return kb.as_markup()