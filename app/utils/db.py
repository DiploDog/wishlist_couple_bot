import logging
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from aiogram import Bot

from config.config import settings
from app.dao.schemas import ProductCreateSchema
from app.dao.dao import ProductDAO, UserDAO
from app.texts import texts

logger = logging.getLogger(__name__)


async def create_product_record(
    session: AsyncSession,
    data: dict,
    telegram_id: int,
    bot: Bot | None = None,
):
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)
    if not user:
        raise ValueError(f"User with telegram_id={telegram_id} not found")

    product_dao = ProductDAO(session)
    product_create_schema = ProductCreateSchema(
        user_id=user.id,
        name=data.get("product_name"),
        price=Decimal(data.get("product_price")),
        url=data.get("url"),
        marketplace=data.get("marketplace"),
        priority=data.get("product_priority"),
    )
    try:
        product = await product_dao.create(product_create_schema)
        await session.commit()

        if bot:
            partner_id = next(
                (uid for uid in settings.allowed_tg_ids if uid != telegram_id), None
            )
            if partner_id:
                try:
                    await bot.send_message(
                        partner_id,
                        texts.PARTNER_ADDED_NOTIFICATION.format(product_name=product.name),
                    )
                except Exception as e:
                    logger.warning(f"Failed to notify partner: {e}")

        return product
    except Exception as e:
        logger.error(f"Error creating product record: {e}", exc_info=True)
        await session.rollback()
        raise