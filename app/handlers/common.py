import logging
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import inject, FromDishka

from app.states.states import AddProductState
from app.texts import texts, cards
from app.utils import parsing, db as db_utils
from app.handlers.helpers import product_answer
from app.kb import enter_product_menu_kb, enter_priority_kb
from app.dao.enums import ProductAddAttrs, ProductAppend, Priority
from app.dao.schemas import ProductReadSchema
from app.dao.dao import UserDAO


INITIAL_PRODUCT_ATTRS_AMOUNT = 3

ATTR_CONFIG = {
    ProductAddAttrs.NAME.value: (texts.PRODUCT_NAME_ENTER, None),
    ProductAddAttrs.PRICE.value: (texts.PRODUCT_PRICE_ENTER, None),
}

PRIORITY_CONFIG = {
    Priority.LOW.value, Priority.MEDIUM.value, Priority.HIGH.value,
}

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
@inject
async def start_command(message: Message, session: FromDishka[AsyncSession]):
    user_dao = UserDAO(session)
    user, created = await user_dao.get_or_create(message.from_user)
    if created:
        await session.commit()
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
    ppu_msg = await message.answer(texts.PRODUCT_ATTRS_ENTER, 
        reply_markup=enter_product_menu_kb(),
    )
    await state.set_data({
        "marketplace": marketplace, 
        "url": url,
    })

@router.callback_query(AddProductState.start_adding)
@inject
async def process_product_attrs(
    callback: CallbackQuery, 
    state: AddProductState, 
    bot: Bot,
    session: FromDishka[AsyncSession]):

    await callback.answer()

    data = await state.get_data()
    cb_data = callback.data

    if cb_data == ProductAddAttrs.PRIORITY.value:
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=texts.PRODUCT_PRIORITY_ENTER,
            reply_markup=enter_priority_kb(),
        )
        return
        
    if cb_data in PRIORITY_CONFIG:
        await state.update_data(product_priority=cb_data)
        updated_data = await state.get_data()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=texts.PRODUCT_ATTRS_ENTER,
            reply_markup=enter_product_menu_kb(updated_data),
        )
        return

    cfg = ATTR_CONFIG.get(cb_data)
    if cfg:
        text, reply_markup = cfg
        await product_answer(
            product_attr=cb_data,
            callback=callback,
            bot=bot,
            state=state,
            state_name=AddProductState,
            message_id=callback.message.message_id,
            text=text,
            reply_markup=reply_markup,
        )
        return

    if cb_data == ProductAppend.CANCEL.value:
        await state.clear()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=texts.PRODUCT_APPEND_CANCEL,
            reply_markup=None,
        )
        return
        
    if cb_data == ProductAppend.CONFIRM.value:
        required_attrs = {attr.value for attr in ProductAddAttrs}
        if not required_attrs.issubset(data.keys()):
            await callback.answer(texts.PRODUCT_ATTRS_NOT_FULL, show_alert=True)
            return

        product = await db_utils.create_product_record(session, data, callback.from_user.id, bot=bot)
        product_schema = ProductReadSchema.model_validate(product)
        await state.clear()
        await callback.answer()

        product_card = cards.PRODUCT_APPEND_CARD.format(
            product_name = product_schema.name,
            product_price = product_schema.price,
            marketplace = product_schema.marketplace.value,
            product_priority = product_schema.priority.value,
            url = product_schema.url,
        )
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=product_card,
            reply_markup=None,
        )


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

    data = await state.get_data()
    await state.set_state(AddProductState.start_adding)
    await message.answer(
        text=texts.PRODUCT_ATTRS_ENTER,
        reply_markup=enter_product_menu_kb(data),
    )
