from typing import Generic, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User as TgUser
from app.dao.schemas import (
    UserCreateSchema, UserUpdateSchema,
    ProductCreateSchema, ProductUpdateSchema
)
from app.dao.models import User, Product
from app.dao.enums import WishlistStatus, Marketplace, Priority, UserRole
from app.dao.base import BaseDAO


class UserDAO(BaseDAO[User, UserCreateSchema, UserUpdateSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create(self, tg_user: TgUser) -> Tuple[User, bool]:
        user = await self.get_by_telegram_id(tg_user.id)
        if user:
            return user, False
        user = await self.create(UserCreateSchema(
            telegram_id=tg_user.id,
            role=UserRole.USER,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        ))
        return user, True

    async def get_by_username(self, username: str) -> Optional[User]:
        if username.startswith("@"):
            username = username[1:]
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

class ProductDAO(BaseDAO[Product, ProductCreateSchema, ProductUpdateSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_user_id(self, user_id: int) -> List[Product]:
        query = select(Product).where(Product.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_status(self, status: WishlistStatus) -> List[Product]:
        query = select(Product).where(Product.whishlist_status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_marketplace(self, marketplace: Marketplace) -> List[Product]:
        query = select(Product).where(Product.marketplace == marketplace)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_priority(self, priority: Priority) -> List[Product]:
        query = select(Product).where(Product.priority == priority)
        result = await self.session.execute(query)
        return list(result.scalars().all())