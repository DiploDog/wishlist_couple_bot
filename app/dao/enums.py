from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class Marketplace(Enum):
    OZON = "ozon"
    WILDBERRIES = "wildberries"
    YAMARKET = "market.yandex"

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

class ProductAddAttrs(Enum):
    NAME = "product_name"
    PRICE = "product_price"
    PRIORITY = "product_priority"