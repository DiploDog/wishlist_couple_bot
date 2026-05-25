from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.dao.models import Product 
from app.kb.pagination import build_pagination_window
from app.kb import buttons
from app.dao.enums import ProductEditAttrs, WishlistStatus, Priority
from app.callbacks.wishlist import (
    WishlistPageCallback, 
    WishlistViewCallback,
    ProductActionCallback,
)


def wishlist_kb(
    products: list[Product],
    owner_tg_id: int,
    page: int,
    total: int,
    page_size: int = 10,
    status_filter: str = "",
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for product in products:
        kb.button(
            text=f"{product.priority.value} {product.name}",
            callback_data=WishlistViewCallback(
                product_id=product.id,
                owner_tg_id=owner_tg_id,
                page=page,
            ),
        )

    # Кнопки фильтрации
    filter_options = [
        (buttons.BUTTON_FILTER_ALL, ""),
        (buttons.BUTTON_FILTER_ACTIVE, WishlistStatus.ACTIVE.value),
        (buttons.BUTTON_FILTER_BOUGHT, WishlistStatus.BOUGHT.value),
    ]
    for label, sf in filter_options:
        display = f"[{label}]" if sf == status_filter else label
        kb.button(
            text=display,
            callback_data=WishlistPageCallback(
                owner_tg_id=owner_tg_id,
                page=1,
                status_filter=sf,
            ),
        )

    pg = build_pagination_window(page=page, total=total, page_size=page_size)

    navigation_count = 0
    if pg.total_pages > 1:
        if pg.have_prev:
            kb.button(
                text=buttons.BUTTON_PREV,
                callback_data=WishlistPageCallback(
                    owner_tg_id=owner_tg_id,
                    page=pg.prev_page,
                    status_filter=status_filter,
                ),
            )
            navigation_count += 1

        for p in pg.pages:
            kb.button(
                text=f"[{p}]" if p == page else str(p),
                callback_data=WishlistPageCallback(
                    owner_tg_id=owner_tg_id,
                    page=p,
                    status_filter=status_filter,
                ),
            )
            navigation_count += 1

        if pg.have_next:
            kb.button(
                text=buttons.BUTTON_NEXT,
                callback_data=WishlistPageCallback(
                    owner_tg_id=owner_tg_id,
                    page=pg.next_page,
                    status_filter=status_filter,
                ),
            )
            navigation_count += 1

    adjust = [1] * len(products) + [3]
    if navigation_count:
        adjust.append(navigation_count)
    kb.adjust(*adjust)

    return kb.as_markup()


def product_card_kb(
    product_id: int,
    owner_tg_id: int,
    page: int,
    is_owner: bool,
) -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    actions: list[tuple[str, str]] = []
    if is_owner:
        actions = [
            (buttons.BUTTON_EDIT_NAME, ProductEditAttrs.EDIT_NAME.value),
            (buttons.BUTTON_EDIT_PRICE, ProductEditAttrs.EDIT_PRICE.value),
            (buttons.BUTTON_EDIT_PRIORITY, ProductEditAttrs.EDIT_PRIORITY.value),
            (buttons.BUTTON_EDIT_STATUS, ProductEditAttrs.EDIT_STATUS.value),
            (buttons.BUTTON_EDIT_DESCRIPTION, ProductEditAttrs.EDIT_DESCRIPTION.value),
            (buttons.BUTTON_EDIT_DELETE, ProductEditAttrs.EDIT_DELETE.value),
        ]
    
        for text, action in actions:
            kb.button(
                text=text,
                callback_data=ProductActionCallback(
                    product_id=product_id,
                    action=action,
                    owner_tg_id=owner_tg_id,
                    page=page,
                )
            )

    kb.button(
        text=buttons.BUTTON_BACK,
        callback_data=WishlistPageCallback(
            owner_tg_id=owner_tg_id,
            page=page,
        ),
    )

    if is_owner:
        pair_rows = len(actions) // 2
        has_tail = len(actions) % 2
        layout = [2] * pair_rows + ([1] if has_tail else []) + [1]
        kb.adjust(*layout)
    else:
        kb.adjust(1)

    return kb.as_markup()


def enter_status_kb(
    product_id: int,
    owner_tg_id: int,
    page: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    statuses = [s for s in WishlistStatus if s != WishlistStatus.DELETED]
    for status in statuses:
        kb.button(
            text=status.value,
            callback_data=ProductActionCallback(
                product_id=product_id,
                action=status.value,
                owner_tg_id=owner_tg_id,
                page=page,
            )
        )
    kb.button(
        text=buttons.BUTTON_CANCEL,
        callback_data=WishlistViewCallback(
            product_id=product_id,
            owner_tg_id=owner_tg_id,
            page=page,
        ),
    )
    n = len(statuses)
    kb.adjust(*([2] * (n // 2)), 1)
    return kb.as_markup()

def edit_priority_kb(
    product_id: int,
    owner_tg_id: int,
    page: int,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for priority in Priority:
        kb.button(
            text=priority.value,
            callback_data=ProductActionCallback(
                product_id=product_id,
                action=priority.value,
                owner_tg_id=owner_tg_id,
                page=page,
            )
        )

    kb.button(
        text=buttons.BUTTON_CANCEL,
        callback_data=WishlistViewCallback(
            product_id=product_id,
            owner_tg_id=owner_tg_id,
            page=page,
        ),
    )
    kb.adjust(3, 1)
    return kb.as_markup()