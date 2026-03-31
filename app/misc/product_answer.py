from aiogram import Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup


async def product_answer(
    product_attr: str, 
    state: State,
    state_name: StatesGroup, 
    bot: Bot,
    callback: CallbackQuery,
    message_id: int,
    text: str,
    reply_markup: ReplyKeyboardMarkup = None):

    await state.update_data(selected_attr=product_attr)
    await state.set_state(state_name.add_attribute)
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=message_id,
        text=text, reply_markup=reply_markup
    )
    await state.set_state(state_name.start_adding)