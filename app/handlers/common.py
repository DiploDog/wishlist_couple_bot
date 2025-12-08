import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import inject, FromDishka

from app.texts import texts
from app.states import ProductParsingState
from app.utils import parsing
from app.kb import product_enter_kb


logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(texts.HELLO.format(
        username=message.from_user.first_name or \
            message.from_user.username
    ))

@router.message(F.text.startswith("https://") or F.text.startswith("http://"))
async def process_product_url(message: Message, state: ProductParsingState):
    url = message.text
    marketplace = parsing.get_marketplace_from_url(url)
    if not marketplace:
        await message.answer(texts.INVALID_URL)
        return
    
    await state.set_data({"marketplace": marketplace})
    await state.set_state(ProductParsingState.start_adding)
    await message.answer(texts.PRODUCT_ATTRS_ENTER, 
        reply_markup=product_enter_kb.enter_product_menu_kb(),
    )

@router.callback_query(ProductParsingState.start_adding, F.data == "product_name")
async def process_product_name(callback: CallbackQuery, state: ProductParsingState):
    await callback.message.answer(texts.PRODUCT_NAME_ENTER)

    
    
