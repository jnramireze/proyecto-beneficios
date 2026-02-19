from bs4 import BeautifulSoup
from datetime import datetime
from scrapers.utils import looks_like_offer

URLS = [
    "https://beneficios.caja18.cl/trabajadores/"
]

def parse_single(html: str, source: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for el in soup.find_all(["a","article","div","li"]):
        text = el.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue
        title_tag = el.find(["h3","h2","strong","b"])
        comercio = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]
        href = el.get("href", "")
        link = href if href.startswith("http") else source
        rows.append({
            "Proveedor": "Caja 18",
            "Categoría": "Caja de Compensación",
            "Comercio": comercio,
            "Beneficio": text,
            "Vigencia": "",
            "Link": link,
            "Fuente": source,
            "Extraido_En": datetime.now().isoformat()
        })
    uniq = {(r["Comercio"], r["Beneficio"]): r for r in rows}
    return list(uniq.values())

def parse_all(html_map: dict):
    out=[]
    for url, html in html_map.items():
        out += parse_single(html, url)
    uniq = {(r["Proveedor"], r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
