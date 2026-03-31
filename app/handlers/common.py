import logging
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import inject, FromDishka

from app.states.states import AddProductState
from app.texts import texts
from app.utils import parsing, db as db_utils
from app.misc import product_answer
from app.kb import enter_product_menu_kb, enter_priority_kb
from app.dao.enums import ProductAddAttrs, ProductAppend


INITIAL_PRODUCT_ATTRS_AMOUNT = 3

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(texts.HELLO.format(
        username=message.from_user.first_name or \
            message.from_user.username
    ))

@router.message(F.text.startswith("https://") or F.text.startswith("http://"))
async def process_product_url(message: Message, state: AddProductState):
    url = message.text
    marketplace = parsing.get_marketplace_from_url(url)
    if not marketplace:
        await message.answer(texts.INVALID_URL)
        return
    
    await state.set_state(AddProductState.start_adding)
    ppu_message_id = await message.answer(texts.PRODUCT_ATTRS_ENTER, 
        reply_markup=enter_product_menu_kb(),
    )
    await state.set_data({
        "marketplace": marketplace, 
        "url": url,
        "ppu_message_id": ppu_message_id.message_id})

@router.callback_query(AddProductState.start_adding)
@inject
async def process_product_attrs(
    callback: CallbackQuery, 
    state: AddProductState, 
    bot: Bot,
    session: FromDishka[AsyncSession]):

    await callback.answer()
    data = await state.get_data()
    ppu_msg_id = data.get("ppu_message_id")
    match callback.data:
        case ProductAddAttrs.NAME.value:
            await product_answer(
                product_attr=ProductAddAttrs.NAME.value,
                callback=callback, bot=bot, state=state, 
                state_name=AddProductState,
                message_id=ppu_msg_id,
                text=texts.PRODUCT_NAME_ENTER,
            )
        case ProductAddAttrs.PRICE.value:
            await product_answer(
                product_attr=ProductAddAttrs.PRICE.value,
                callback=callback, bot=bot, state=state, 
                state_name=AddProductState,
                message_id=ppu_msg_id,
                text=texts.PRODUCT_PRICE_ENTER,
            )
        case ProductAddAttrs.PRIORITY.value:
            await product_answer(
                product_attr=ProductAddAttrs.PRIORITY.value,
                callback=callback, bot=bot, state=state, 
                state_name=AddProductState,
                message_id=ppu_msg_id,
                text=texts.PRODUCT_PRIORITY_ENTER,
                # TODO: добавить новую клавиатуру с приоритетами
                reply_markup=enter_priority_kb(),
            )
        case ProductAppend.CANCEL.value:
            await state.clear()
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=texts.PRODUCT_APPEND_CANCEL,
                reply_markup=None,
            )
        case ProductAppend.CONFIRM.value:
            if INITIAL_PRODUCT_ATTRS_AMOUNT > \
                sum(value.startswith("product") for value in data):
                await callback.answer(texts.PRODUCT_ATTRS_NOT_FULL, show_alert=True)
                return
            
            await db_utils.create_product_record(session, data)
            await state.clear()
            await callback.answer(texts.PRODUCT_APPEND_SUCCESS, show_alert=True)
            


@router.message(AddProductState.add_attribute)
async def add_product_attribute(message: Message, state: AddProductState):
    data = await state.get_data()
    logger.info(f"Data: {data}")
    selected_attr = data.get("selected_attr")

    match selected_attr:
        case ProductAddAttrs.NAME.value:
            await state.update_data(product_name=message.text)
        case ProductAddAttrs.PRICE.value:
            await state.update_data(product_price=message.text)
        case ProductAddAttrs.PRIORITY.value:
            await state.update_data(product_priority=message.text)

    data = await state.get_data()
    await state.set_state(AddProductState.start_adding)
    await message.answer(
        text=texts.PRODUCT_ATTRS_ENTER,
        reply_markup=enter_product_menu_kb(data),
    )