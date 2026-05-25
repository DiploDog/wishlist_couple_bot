import logging
from aiogram import Router
from aiogram.types import ErrorEvent
from app.texts import texts

logger = logging.getLogger(__name__)
error_router = Router()


@error_router.error()
async def error_handler(event: ErrorEvent) -> None:
    logger.error("Unhandled exception in handler", exc_info=event.exception)
    try:
        if event.update.message:
            await event.update.message.answer(texts.UNHANDLED_ERROR)
        elif event.update.callback_query:
            await event.update.callback_query.answer(texts.UNHANDLED_ERROR, show_alert=True)
    except Exception:
        pass
