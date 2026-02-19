from bs4 import BeautifulSoup
from datetime import datetime

URLS = [
    "https://www.caja18.cl/beneficios/",          # landing de beneficios
    "https://beneficios.caja18.cl/trabajadores/"  # portal de beneficios destacados
]

def parse_single(html:str, source:str):
    soup = BeautifulSoup(html, "html.parser")
    data = []
    for card in soup.find_all(["a","article","div","li"]):
        txt = card.get_text(" ", strip=True)
        if not txt:
            continue
        low = txt.lower()
        if any(kw in low for kw in ["beneficio","descuento","hasta","$","cine","farmacia","dental","gasco","lipigas","entel conviene"]):
            if 20 <= len(txt) <= 500:
                title_tag = card.find(["h3","h2","strong","b"])
                title = title_tag.get_text(strip=True) if title_tag else txt.split(".")[0][:80]
                href = card.get("href", "")
                link = href if href and href.startswith("http") else source
                data.append({
                    "Proveedor": "Caja 18",
                    "Categoría": "Caja de Compensación",
                    "Comercio": title,
                    "Beneficio": txt,
                    "Vigencia": "",
                    "Link": link,
                    "Fuente": source,
                    "Extraido_En": datetime.now().isoformat()
                })
    uniq = {(d["Comercio"], d["Beneficio"]): d for d in data}
    return list(uniq.values())

def parse_all(html_map:dict):
    all_rows = []
    for url, html in html_map.items():
        all_rows += parse_single(html, url)
    return all_rows

