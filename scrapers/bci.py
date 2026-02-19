from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.bci.cl/beneficios/beneficios-bci"  # portal público Bci Beneficios

def parse_bci(html:str):
    soup = BeautifulSoup(html, "html.parser")
    data = []
    for card in soup.find_all(["a","article","div","li"]):
        txt = card.get_text(" ", strip=True)
        if not txt:
            continue
        low = txt.lower()
        if any(kw in low for kw in ["descuento","cashback","cuotas sin interés","restaurantes","viajes","beneficios bci"]):
            if 25 <= len(txt) <= 500:
                title_tag = card.find(["h3","h2","strong","b"])
                title = title_tag.get_text(strip=True) if title_tag else txt.split(".")[0][:80]
                href = card.get("href", "")
                link = href if href and href.startswith("http") else URL
                data.append({
                    "Proveedor": "Bci - Beneficios",
                    "Categoría": "Bancos/TC",
                    "Comercio": title,
                    "Beneficio": txt,
                    "Vigencia": "",
                    "Link": link,
                    "Fuente": URL,
                    "Extraido_En": datetime.now().isoformat()
                })
    uniq = {(d["Comercio"], d["Beneficio"]): d for d in data}
    return list(uniq.values())

