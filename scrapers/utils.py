import re

OFFER_RE = re.compile(r"(\\d+%|\\$\\d{3,}|dcto|descuento|cuotas\\s+sin\\s+interés|cashback)", re.IGNORECASE)
BLACKLIST_RE = re.compile(r"(No encontramos beneficios|Descarga la App|Mi Movistar|Productos y Servicios|Personas Emprendedores|¿Qué día vas|Ayuda)", re.IGNORECASE)

def looks_like_offer(text: str) -> bool:
    if not text: 
        return False
    if BLACKLIST_RE.search(text):
        return False
    return bool(OFFER_RE.search(text))
