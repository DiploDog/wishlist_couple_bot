from aiogram.filters.callback_data import CallbackData


class WishlistPageCallback(CallbackData, prefix="wishlist_page"):
    owner_tg_id: int
    page: int


class WishlistViewCallback(CallbackData, prefix="wishlist_view"):
    product_id: int
    owner_tg_id: int
    page: int


class ProductActionCallback(CallbackData, prefix="wishlist_action"):
    product_id: int
    action: str
    owner_tg_id: int
    page: int

