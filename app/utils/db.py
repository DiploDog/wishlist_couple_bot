import logging
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.dao.schemas import ProductCreateSchema
from app.dao.dao import ProductDAO, UserDAO

logger = logging.getLogger(__name__)

async def create_product_record(session: AsyncSession, data: dict, telegram_id: int):
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
        await product_dao.create(product_create_schema)
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error creating product record: {e}", exc_info=True)
        await session.rollback()
        raise