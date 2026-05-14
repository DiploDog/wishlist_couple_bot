import logging
import asyncio
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import inject, FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from app.texts import cards, texts
from app.dao.dao import ProductDAO
from app.dao.schemas import ProductReadSchema

logger = logging.get_logger(__name__)


wishlist_router = Router()

@wishlist_router.message(Command("wishlist"))
@inject
async def show_last_added_products(message: Message, session: FromDishka[AsyncSession]):
    product_dao = ProductDAO(session)
    last_product = await product_dao.get_last_added(message.from_user.id)
    if last_product:
        product_schema = ProductReadSchema.model_validate(last_product)
        product_card = cards.LAST_ADDED_PRODUCT_CARD.format(
            product_name=product_schema.name,
            product_price=product_schema.price,
            marketplace=product_schema.marketplace.value,
            product_priority=product_schema.priority.value,
            url=product_schema.url,
        )
        await message.answer(product_card)
    else:
        await message.answer(texts.PRODUCT_NOT_FOUND)