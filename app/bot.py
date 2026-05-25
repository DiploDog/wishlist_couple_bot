import logging
from config.config import settings
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from app.handlers.common import router as common_router
from app.handlers.wishlist import wishlist_router
from app.handlers.errors import error_router
from app.providers import DataBaseProvider, RedisProvider
from app.middlewares.restriction import WhitelistMiddleware


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )

    dp = Dispatcher(
        storage=RedisStorage.from_url(
            settings.redis_url,
            key_builder=DefaultKeyBuilder(
                with_destiny=True
            )
        )
    )

    container = make_async_container(
        DataBaseProvider(),
        RedisProvider(),
    )

    dp.include_router(common_router)
    dp.include_router(wishlist_router)
    dp.include_router(error_router)

    dp.update.middleware(WhitelistMiddleware(allowed_user_ids=settings.allowed_tg_ids))

    # dp.message / dp.callback_query / dp.errors middlewares

    setup_dishka(container=container, router=dp)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=[
            BotCommand(command="mywishlist", description="Мой вишлист"),
            BotCommand(command="wishlist",   description="Вишлист партнёра"),
            BotCommand(command="showlast",   description="Последний добавленный товар"),
        ])
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error starting bot: {e}", exc_info=True)
    finally:
        await bot.session.close()
        await container.close()