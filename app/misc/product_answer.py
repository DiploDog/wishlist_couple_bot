from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery


async def product_answer(
    product_attr: str, 
    state: State,
    state_name: str, 
    bot: Bot,
    callback: CallbackQuery,
    message_id: int,
    text: str):

    await state.update_data(selected_attr=product_attr)
    await state.set_state(state_name)
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text=text.PRODUCT_NAME_ENTER,
        reply_markup=None
    )