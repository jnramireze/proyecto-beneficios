from bs4 import BeautifulSoup
from datetime import datetime
from scrapers.utils import looks_like_offer

URL = "https://www.bci.cl/beneficios/beneficios-bci"

def parse_bci(html: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for el in soup.find_all(["a","article","div","li"]):
        text = el.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue
        title_tag = el.find(["h3","h2","strong","b"])
        comercio = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]
        href = el.get("href", "")
        link = href if href.startswith("http") else URL
        out.append({
            "Proveedor": "Bci - Beneficios",
            "Categoría": "Bancos/TC",
            "Comercio": comercio,
            "Beneficio": text,
            "Vigencia": "",
            "Link": link,
            "Fuente": URL,
            "Extraido_En": datetime.now().isoformat()
        })
    uniq = {(r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
