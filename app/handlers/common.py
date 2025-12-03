import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import inject, FromDishka

from app.texts import texts


logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(texts.HELLO.format(
        username=message.from_user.first_name or \
            message.from_user.username
    ))

@router.message(F.text.startswith("https://") or F.text.startswith("http://"))
async def process_product_url(message: Message):