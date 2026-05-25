import logging
from decimal import Decimal, InvalidOperation
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dishka.integrations.aiogram import inject, FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.helpers import _get_partner_tg_id, render_product_list
from app.kb.wishlist_kb import wishlist_kb, product_card_kb, enter_status_kb, edit_priority_kb
from app.kb.common import confirm_kb
from app.texts import cards, texts
from app.states.states import EditProductState
from app.dao.enums import ProductEditAttrs, WishlistStatus, Priority
from app.dao.dao import ProductDAO, UserDAO
from app.dao.schemas import ProductReadSchema, ProductUpdateSchema
from app.callbacks.wishlist import (
    WishlistPageCallback,
    WishlistViewCallback,
    ProductActionCallback,
    DeleteConfirmCallback,
)


ACTION_PROMPT = {
    ProductEditAttrs.EDIT_NAME: texts.PRODUCT_NAME_ENTER,
    ProductEditAttrs.EDIT_PRICE: texts.PRODUCT_PRICE_ENTER,
    ProductEditAttrs.EDIT_DESCRIPTION: texts.PRODUCT_DESCRIPTION_ENTER,
}

STATUS_MAP = {s.value: s for s in WishlistStatus if s != WishlistStatus.DELETED}
PRIORITY_MAP = {p.value: p for p in Priority}

logger = logging.getLogger(__name__)
wishlist_router = Router()


async def _show_updated_card(
    callback: CallbackQuery,
    session: AsyncSession,
    product_id: int,
    owner_tg_id: int,
    page: int,
):
    product_dao = ProductDAO(session)
    product = await product_dao.get(product_id)
    viewer = await UserDAO(session).get_by_telegram_id(callback.from_user.id)

    if not product or not viewer:
        await callback.message.edit_text(texts.PRODUCT_NOT_FOUND)
        return

    is_owner = product.user_id == viewer.id
    card_text = cards.PRODUCT_VIEW_CARD.format(
        product_name=product.name,
        description=product.description or "-",
        product_price=product.price,
        marketplace=product.marketplace.value,
        product_priority=product.priority.value,
        status=product.whishlist_status.value,
        url=product.url,
    )
    await callback.message.edit_text(
        card_text,
        reply_markup=product_card_kb(
            product_id=product.id,
            is_owner=is_owner,
            owner_tg_id=owner_tg_id,
            page=page,
        ),
    )

@wishlist_router.message(Command("showlast"))
@inject
async def show_last_added_products(message: Message, session: FromDishka[AsyncSession]):
    
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(texts.USER_NOT_FOUND)
        return

    product_dao = ProductDAO(session)
    last_product = await product_dao.get_last_added(user.id)
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


@wishlist_router.message(Command("mywishlist"))
@inject
async def my_wishlist_command(message: Message, session: FromDishka[AsyncSession]):
    await render_product_list(
        session=session,
        tg_owner_id=message.from_user.id,
        page=1, 
        message=message,
    )

@wishlist_router.message(Command("wishlist"))
@inject
async def partner_wishlist_command(message: Message, session: FromDishka[AsyncSession]):
    owner_id = message.from_user.id
    partner_id = _get_partner_tg_id(owner_id)
    if not partner_id:
        await message.answer(texts.USER_NOT_FOUND)
        return
    await render_product_list(
        session=session,
        tg_owner_id=partner_id,
        page=1,
        message=message
    )

@wishlist_router.callback_query(WishlistViewCallback.filter())
@inject
async def view_product(
    callback: CallbackQuery,
    callback_data: WishlistViewCallback,
    session: FromDishka[AsyncSession]
):
    await callback.answer()
    user_dao = UserDAO(session)
    viewer = await user_dao.get_by_telegram_id(callback.from_user.id)
    product_dao = ProductDAO(session)
    product = await product_dao.get(callback_data.product_id)

    if not viewer or not product:
        await callback.message.edit_text(texts.PRODUCT_NOT_FOUND)
        return
    
    is_owner = product.user_id == viewer.id
    card_text = cards.PRODUCT_VIEW_CARD.format(
        product_name=product.name,
        description=product.description or "-",
        product_price=product.price,
        marketplace=product.marketplace.value,
        product_priority=product.priority.value,
        status=product.whishlist_status.value,
        url=product.url,
    )

    await callback.message.edit_text(
        card_text,
        reply_markup=product_card_kb(
            product_id=product.id,
            is_owner=is_owner,
            owner_tg_id=callback_data.owner_tg_id,
            page=callback_data.page,
        )
    )

@wishlist_router.callback_query(WishlistPageCallback.filter())
@inject
async def wishlist_page(
    callback: CallbackQuery,
    callback_data: WishlistPageCallback,
    session: FromDishka[AsyncSession]
):
    await callback.answer()
    await render_product_list(
        session=session,
        tg_owner_id=callback_data.owner_tg_id,
        page=callback_data.page,
        callback=callback,
        status_filter=callback_data.status_filter,
    )

@wishlist_router.callback_query(ProductActionCallback.filter())
@inject
async def edit_product(
    callback: CallbackQuery,
    callback_data: ProductActionCallback,
    session: FromDishka[AsyncSession],
    state: FSMContext,
):
    await callback.answer()
    product_dao = ProductDAO(session)
    product = await product_dao.get(callback_data.product_id)
    if not product:
        await callback.message.edit_text(texts.PRODUCT_NOT_FOUND)
        return

    action = callback_data.action

    # Нажата кнопка конкретного статуса — сразу обновляем БД
    if action in STATUS_MAP:
        new_status = STATUS_MAP[action]
        await product_dao.update(product.id, ProductUpdateSchema(whishlist_status=new_status))
        await session.commit()
        await state.clear()

        await _show_updated_card(callback, session, product.id, callback_data.owner_tg_id, callback_data.page)
        return

    # Нажата кнопка конкретного приоритета — сразу обновляем БД
    if action in PRIORITY_MAP:
        await product_dao.update(product.id, ProductUpdateSchema(priority=PRIORITY_MAP[action]))
        await session.commit()
        await state.clear()
        await _show_updated_card(callback, session, product.id, callback_data.owner_tg_id, callback_data.page)
        return

    # Определяем prompt и reply_markup для текстового ввода или подтверждения
    if action == ProductEditAttrs.EDIT_DELETE:
        prompt = texts.PRODUCT_DELETE_PROMPT
        reply_markup = confirm_kb(
            confirm_callback=DeleteConfirmCallback(confirmed=True).pack(),
            cancel_callback=DeleteConfirmCallback(confirmed=False).pack(),
        )
    elif action == ProductEditAttrs.EDIT_PRIORITY:
        prompt = texts.PRODUCT_PRIORITY_ENTER
        reply_markup = edit_priority_kb(
            product_id=product.id,
            owner_tg_id=callback_data.owner_tg_id,
            page=callback_data.page,
        )
    elif action == ProductEditAttrs.EDIT_STATUS:
        prompt = texts.PRODUCT_STATUS_ENTER
        reply_markup = enter_status_kb(
            product_id=product.id,
            owner_tg_id=callback_data.owner_tg_id,
            page=callback_data.page,
        )
    else:
        prompt = ACTION_PROMPT.get(action)
        if not prompt:
            return
        reply_markup = None

    await state.set_state(EditProductState.edit_field)
    await state.update_data(
        product_id=product.id,
        action=action,
        owner_tg_id=callback_data.owner_tg_id,
        page=callback_data.page,
    )
    await callback.message.edit_text(prompt, reply_markup=reply_markup)


@wishlist_router.message(EditProductState.edit_field, F.text)
@inject
async def apply_text_edit(
    message: Message,
    state: FSMContext,
    session: FromDishka[AsyncSession],
):
    data = await state.get_data()
    product_id = data["product_id"]
    action = data["action"]
    owner_tg_id = data["owner_tg_id"]
    page = data["page"]

    update_kwargs = {}
    if action == ProductEditAttrs.EDIT_NAME:
        update_kwargs["name"] = message.text
    elif action == ProductEditAttrs.EDIT_PRICE:
        try:
            update_kwargs["price"] = Decimal(message.text.replace(",", "."))
        except InvalidOperation:
            await message.answer(texts.PRODUCT_PRICE_INVALID)
            return
    elif action == ProductEditAttrs.EDIT_DESCRIPTION:
        update_kwargs["description"] = message.text
    else:
        return

    product_dao = ProductDAO(session)
    await product_dao.update(product_id, ProductUpdateSchema(**update_kwargs))
    await session.commit()
    await state.clear()

    product = await product_dao.get(product_id)
    viewer = await UserDAO(session).get_by_telegram_id(message.from_user.id)
    is_owner = product.user_id == viewer.id
    card_text = cards.PRODUCT_VIEW_CARD.format(
        product_name=product.name,
        description=product.description or "-",
        product_price=product.price,
        marketplace=product.marketplace.value,
        product_priority=product.priority.value,
        status=product.whishlist_status.value,
        url=product.url,
    )
    await message.answer(texts.EDIT_SUCCESS)
    await message.answer(
        card_text,
        reply_markup=product_card_kb(
            product_id=product.id,
            is_owner=is_owner,
            owner_tg_id=owner_tg_id,
            page=page,
        ),
    )


@wishlist_router.callback_query(DeleteConfirmCallback.filter())
@inject
async def confirm_delete(
    callback: CallbackQuery,
    callback_data: DeleteConfirmCallback,
    state: FSMContext,
    session: FromDishka[AsyncSession],
):
    await callback.answer()
    data = await state.get_data()
    product_id = data["product_id"]
    owner_tg_id = data["owner_tg_id"]
    page = data["page"]

    if not callback_data.confirmed:
        await state.clear()
        await _show_updated_card(callback, session, product_id, owner_tg_id, page)
        return

    product_dao = ProductDAO(session)
    await product_dao.update(product_id, ProductUpdateSchema(whishlist_status=WishlistStatus.DELETED))
    await session.commit()
    await state.clear()
    await callback.message.edit_text(texts.PRODUCT_DELETED)


@wishlist_router.message(EditProductState.edit_field)
async def edit_field_invalid_input(message: Message) -> None:
    await message.answer(texts.EDIT_INVALID_INPUT)