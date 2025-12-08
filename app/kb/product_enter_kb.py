from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


def enter_product_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="❌ Название", callback_data="product_name"),
        InlineKeyboardButton(text="❌ Цена", callback_data="product_price"),
        InlineKeyboardButton(text="❌ Приоритет", callback_data="product_priority"),
    )
    kb.row(
        InlineKeyboardButton(text="🔙 Отмена", callback_data="product_cancel")
    )
    return kb.as_markup()