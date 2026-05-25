from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.dao import UserDAO, ProductDAO
from app.kb.wishlist_kb import wishlist_kb
from app.texts import texts


async def render_product_list(
    session: AsyncSession,
    tg_owner_id: int,
    page: int,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
    status_filter: str = "",
):
    user_dao = UserDAO(session)
    owner = await user_dao.get_by_telegram_id(tg_owner_id)
    if not owner:
        if message:
            await message.answer(texts.USER_NOT_FOUND)
        return

    product_dao = ProductDAO(session)
    products = await product_dao.get_by_user_id(owner.id, page, status_filter=status_filter)
    total = await product_dao.count_by_user_id(owner.id, status_filter=status_filter)

    if not products:
        text = texts.PRODUCT_NOT_FOUND
        if message:
            await message.answer(text)
        elif callback:
            await callback.message.edit_text(text, reply_markup=None)
        return

    markup = wishlist_kb(products, tg_owner_id, page, total, status_filter=status_filter)
    if message:
        await message.answer(texts.CHOOSE_WISH, reply_markup=markup)
    elif callback:
        await callback.message.edit_text(texts.CHOOSE_WISH, reply_markup=markup) 