from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


class WhitelistMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_ids: list[int]) -> None:
        self.allowed_user_ids = allowed_user_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")

        if user is None or user.id not in self.allowed_user_ids:
            if isinstance(event, Message):
                await event.answer("Этот бот только для своих 🙂")
            elif isinstance(event, CallbackQuery):
                await event.answer("Нет доступа", show_alert=True)

            return None

        return await handler(event, data)