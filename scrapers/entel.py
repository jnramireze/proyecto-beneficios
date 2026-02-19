from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.entel.cl/beneficios"   # ← vuelve a declarar la constante

# Dentro de parse_entel, reemplaza el bucle principal por este:

def parse_entel(html:str):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Busca tarjetas de beneficios por clases comunes y por contenido semántico
    candidates = soup.find_all(["section","div","article","li","a"])
    for c in candidates:
        text = c.get_text(" ", strip=True)
        if not text: 
            continue
        low = text.lower()
        if any(k in low for k in ["descuento", "beneficio", "club entel", "%", "dcto", "promoción", "entradas"]):
            if 20 <= len(text) <= 600:
                # Categoría deducida por heading más cercano
                cat = "Beneficios"
                parent = c.find_parent(["section","div"])
                if parent:
                    h = parent.find(["h2","h3"])
                    if h and 2 <= len(h.get_text(strip=True)) <= 60:
                        cat = h.get_text(strip=True)

                title_tag = c.find(["h3","h2","strong","b"])
                titulo = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]

                a = c.find("a")
                href = a.get("href") if a else ""
                link = href if href.startswith("http") else "https://www.entel.cl/beneficios"

                data.append({
                    "Proveedor":"Entel - Club Entel",
                    "Categoría": cat,
                    "Comercio": titulo,
                    "Beneficio": text,
                    "Vigencia": "",
                    "Link": link,
                    "Fuente": "https://www.entel.cl/beneficios",
                    "Extraido_En": datetime.now().isoformat()
                })

    uniq = {(d["Comercio"], d["Beneficio"]): d for d in data}
    return list(uniq.values())
