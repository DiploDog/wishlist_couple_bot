from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import (
    Integer, DateTime, String, Numeric,
    BigInteger, ForeignKey,
    Enum as SQLEnum)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped,
    mapped_column, relationship,
    declared_attr,
)

from app.dao.enums import UserRole, Marketplace, WishlistStatus, Priority


class Base(AsyncAttrs, DeclarativeBase):
    "Base class for all app-models"

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=None, onupdate=datetime.now(tz=timezone.utc))

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class User(Base):
    "User model"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String)

    products: Mapped[List["Product"]] = relationship(
        back_populates="user", 
        foreign_keys="Product.user_id",
        cascade="all, delete-orphan")


class Product(Base):
    "Product model"
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    marketplace: Mapped[Marketplace] = mapped_column(
        SQLEnum(Marketplace), nullable=False)
    whishlist_status: Mapped[WishlistStatus] = mapped_column(
        SQLEnum(WishlistStatus), nullable=False, 
        default=WishlistStatus.ACTIVE)
    priority: Mapped[Priority] = mapped_column(SQLEnum(Priority))
    description: Mapped[Optional[str]] = mapped_column(String)
    image_url: Mapped[Optional[str]] = mapped_column(String)