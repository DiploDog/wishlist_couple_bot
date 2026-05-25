from pydantic import BaseModel, ConfigDict
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
    user_id: int
    name: str
    price: Decimal
    url: str
    marketplace: Marketplace
    whishlist_status: WishlistStatus = WishlistStatus.ACTIVE
    priority: Priority
    description: Optional[str] = None
    image_url: Optional[str] = None

class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    marketplace: Optional[Marketplace] = None
    image_url: Optional[str] = None
    whishlist_status: Optional[WishlistStatus] = None
    priority: Optional[Priority] = None

class ProductReadSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    name: str
    price: Decimal
    url: str
    marketplace: Marketplace
    whishlist_status: WishlistStatus
    priority: Priority
    description: Optional[str] = None
    image_url: Optional[str] = None
