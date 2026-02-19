# scrapers/utils.py
import re

# Acepta si hay % o $ o términos típicos de beneficio
OFFER_RE = re.compile(r"(\d+%|\$\d{3,}|dcto|descuento|cuotas\s+sin\s+interés|cashback)", re.IGNORECASE)
# Excluye menús y texto genérico que “ensucia” el set
BLACKLIST_RE = re.compile(
    r"(No encontramos beneficios|Descarga la App|Mi Entel|Mi Movistar|"
    r"Productos y Servicios|Personas Emprendedores|¿Qué día vas|Ayuda|Sigue tu Compra)",
    re.IGNORECASE
)

def looks_like_offer(text: str) -> bool:
    if not text:
        return False
    if BLACKLIST_RE.search(text):
        return False
    return bool(OFFER_RE.search(text))
