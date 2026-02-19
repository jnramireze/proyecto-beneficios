from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.entel.cl/beneficios"  # catálogo público Club Entel

def parse_entel(html:str):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Heurística: busca secciones y tarjetas con títulos/links
    for sec in soup.find_all(["section","div"]):
        # categoría aproximada por heading
        h = sec.find(["h2","h3"])
        categoria = h.get_text(strip=True) if h else "Beneficios"
        cards = sec.find_all(["article","div"], class_=lambda c: c and any(k in c.lower() for k in ["card","benef"]))
        for c in cards:
            titulo_tag = c.find(["h3","h2","strong"])
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
            detalle_tag = c.find(["p","span"])
            detalle = detalle_tag.get_text(strip=True) if detalle_tag else ""
            a = c.find("a")
            href = a.get("href") if a else URL
            if titulo:
                data.append({
                    "Proveedor":"Entel - Club Entel",
                    "Categoría": categoria,
                    "Comercio": titulo,
                    "Beneficio": detalle,
                    "Vigencia": "",
                    "Link": href if href.startswith("http") else f"https://www.entel.cl{href}",
                    "Fuente": URL,
                    "Extraido_En": datetime.now().isoformat()
                })
    # dedup
    uniq = {(d["Comercio"], d["Beneficio"]): d for d in data}
    return list(uniq.values())

