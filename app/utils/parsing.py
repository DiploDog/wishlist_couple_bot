from app.dao.enums import Marketplace


def get_marketplace_from_url(url: str) -> Marketplace:
    if Marketplace.OZON in url:
        return Marketplace.OZON
    elif Marketplace.WILDBERRIES in url:
        return Marketplace.WILDBERRIES
    elif Marketplace.YAMARKET in url:
        return Marketplace.YAMARKET
    else:
        return None