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

class ProductAppend(Enum):
    CONFIRM = "product_confirm"
    CANCEL = "product_cancel"

class ProductEditAttrs(str, Enum):
    EDIT_NAME = "edit_name"
    EDIT_PRICE = "edit_price"
    EDIT_PRIORITY = "edit_priority"
    EDIT_STATUS = "edit_status"
    EDIT_DESCRIPTION = "edit_description"
    EDIT_DELETE = "edit_delete"