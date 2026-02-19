from bs4 import BeautifulSoup
from datetime import datetime
from scrapers.utils import looks_like_offer
import re

URLS = [
    "https://ww2.movistar.cl/app/club/",
    "https://www.movistar.cl/?club-movistar/beneficios/todos"
]

BRAND_RE = re.compile(
    r"(uber|cin[eé]polis|cinemark|cineplanet|melt|accesorios\\s+movistar|gmo|opv|econ[oó]pticas|wetransport|mercado\\s+libre)",
    re.IGNORECASE
)

def parse_movistar(html: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for b in soup.find_all(["div","section","article","li","a","span"]):
        text = b.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue

        # Comercio por marca si aparece; si no, usa heading/primer token
        title_tag = b.find(["h3","h2","strong","b"])
        m = BRAND_RE.search(text)
        comercio = (m.group(1).title() if m else (title_tag.get_text(strip=True) if title_tag else text.split(" ")[0][:60]))
        # Link base (la landing), Movistar no siempre da href por item
        out.append({
            "Proveedor": "Movistar - Club Movistar",
            "Categoría": "Promos/Descuentos",
            "Comercio": comercio,
            "Beneficio": text,
            "Vigencia": "",
            "Link": "https://ww2.movistar.cl/app/club/",
            "Fuente": "https://ww2.movistar.cl/app/club/",
            "Extraido_En": datetime.now().isoformat()
        })
    uniq = {(d["Comercio"], d["Beneficio"]): d for d in out}
    return list(uniq.values())
