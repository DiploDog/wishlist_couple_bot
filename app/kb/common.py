from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


def confirm_kb(
    confirm_callback: str,
    cancel_callback: str,
    confirm_text: str = "✅ Подтвердить",
    cancel_text: str = "❌ Отменить",
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback),
        InlineKeyboardButton(text=cancel_text, callback_data=cancel_callback),
    )
    return kb.as_markup()