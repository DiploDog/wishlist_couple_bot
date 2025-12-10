from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from app.dao.enums import ProductAddAttrs, ProductAppend
from app.kb import buttons

def enter_product_menu_kb(data: dict = {}) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text=f"{'✅' if ProductAddAttrs.NAME.value in data else '❌'} {buttons.BUTTON_NAME}", 
            callback_data=ProductAddAttrs.NAME.value),
        InlineKeyboardButton(
            text=f"{'✅' if ProductAddAttrs.PRICE.value in data else '❌'} {buttons.BUTTON_PRICE}", 
            callback_data=ProductAddAttrs.PRICE.value),
        InlineKeyboardButton(
            text=f"{'✅' if ProductAddAttrs.PRIORITY.value in data else '❌'} {buttons.BUTTON_PRIORITY}", 
            callback_data=ProductAddAttrs.PRIORITY.value),
    )
    kb.row(
        InlineKeyboardButton(
            text=buttons.BUTTON_CONFIRM,
            callback_data=ProductAppend.CONFIRM.value),
        InlineKeyboardButton(
            text=buttons.BUTTON_CANCEL, 
            callback_data=ProductAppend.CANCEL.value)
    )
    return kb.as_markup()