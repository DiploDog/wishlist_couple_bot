from config.config import settings

def _get_partner_tg_id(tg_owner_id: int) -> int | None:
    partner_tg_id = [uid for uid in settings.allowed_tg_ids if uid != tg_owner_id]
    return partner_tg_id[0] if partner_tg_id else None