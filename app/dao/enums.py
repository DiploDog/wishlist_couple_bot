from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class Marketplace(Enum):
    OZON = "ozon"
    WILDBERRIES = "wb"
    YAMARKET = "yandex.market"

class WishlistStatus(Enum):
    ACTIVE = "не куплен"
    BOUGHT = "куплен"
    GIVEN = "подарен"
    REJECTED = "перехотелось"
    DELETED = "удален"

class Priority(Enum):
    LOW = "❤️"
    MEDIUM = "❤️❤️"
    HIGH = "❤️❤️❤️"