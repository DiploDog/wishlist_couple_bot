from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

from app.dao.enums import Marketplace, WishlistStatus, UserRole, Priority


class UserCreateSchema(BaseModel):
    telegram_id: int
    role: UserRole
    username: Optional[str] = None
    first_name: Optional[str]
    last_name: Optional[str] = None

class UserUpdateSchema(BaseModel):
    role: Optional[UserRole] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserReadSchema(BaseModel):
    telegram_id: int
    role: UserRole
    first_name: Optional[str]

class ProductCreateSchema(BaseModel):
    name: str
    price: Decimal
    url: str
    marketplace: Marketplace
    whishlist_status: WishlistStatus = WishlistStatus.ACTIVE
    priority: Priority = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class ProductUpdateSchema(BaseModel):
    price: Optional[Decimal] = None
    marketplace: Optional[Marketplace] = None
    image_url: Optional[str] = None
    whishlist_status: Optional[WishlistStatus] = None
    priority: Optional[Priority] = None

class ProductReadSchema(BaseModel):
    name: str
    price: Decimal
    url: str
    marketplace: Marketplace
    whishlist_status: WishlistStatus
    priority: Priority
    description: Optional[str] = None
    image_url: Optional[str] = None