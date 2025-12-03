from typing import Generic, List, Optional
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.base import BaseDAO
from app.dao.schemas import (
    UserCreateSchema, UserUpdateSchema,
    ProductCreateSchema, ProductUpdateSchema
)
from app.dao.models import User, Product
from app.dao.enums import WishlistStatus, Marketplace, Priority


class UserDAO(Generic[User, UserCreateSchema, UserUpdateSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        if username.startswith("@"):
            username = username[1:]
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

class ProductDAO(Generic[Product, ProductCreateSchema, ProductUpdateSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)
    
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