# whitelist.py
from urllib.parse import urlparse

ALLOWED_HOSTS = {
    "entel.cl",
    "ww2.movistar.cl", "movistar.cl",
    "bci.cl",
    "caja18.cl", "beneficios.caja18.cl",
    "sitiospublicos.bancochile.cl",
    "start.bancoestado.cl", "bancoestado.cl", "rutpay.cl"
}

def is_allowed(url: str) -> bool:
    try:
        host = urlparse(url).netloc.replace("www.", "")
        return host in ALLOWED_HOSTS
    except:
        return False
