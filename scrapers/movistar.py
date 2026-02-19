from bs4 import BeautifulSoup
from datetime import datetime
import re
from collections import defaultdict
from scrapers.utils import looks_like_offer

URLS = [
    "https://ww2.movistar.cl/app/club/",
    "https://www.movistar.cl/?club-movistar/beneficios/todos"
]

def parse_movistar(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tmp = []
    for el in soup.find_all(["div","section","article","li","a","span"]):
        text = el.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue
        title_tag = el.find(["h3","h2","strong","b"])
        comercio = title_tag.get_text(strip=True) if title_tag else text.split(" ")[0][:60]
        tmp.append({
            "Proveedor":"Movistar - Club Movistar",
            "Categoría":"Promos/Descuentos",
            "Comercio": comercio,
            "Beneficio": text,
            "Vigencia": "",
            "Link": "https://ww2.movistar.cl/app/club/",
            "Fuente": "https://ww2.movistar.cl/app/club/",
            "Extraido_En": datetime.now().isoformat()
        })

    # Compactar: 1 por marca con rango de %/$ (Uber, Cinépolis, Melt, Accesorios Movistar, GMO/OPV/Econópticas, Mercado Libre)
    brands = ["Uber","Cinépolis","Cinemark","Cineplanet","Melt","Accesorios Movistar","GMO","OPV","Econópticas","Mercado Libre","Wetransport"]
    groups = defaultdict(list)
    for r in tmp:
        blob = f"{r['Comercio']} {r['Beneficio']}".lower()
        brand = None
        for b in brands:
            if b.lower().replace(" ", "") in blob.replace(" ", ""):
                brand = b
                break
        if not brand:
            continue
        groups[brand].append(r["Beneficio"])

    out=[]
    for b, texts in groups.items():
        alltxt = " ".join(texts)
        pcts = sorted(set(int(x) for x in re.findall(r'(\\d+)%', alltxt)))
        amts = sorted(set(re.findall(r'\\$\\s?\\d{1,3}(?:[\\.,]\\d{3})*', alltxt)))
        if pcts:
            resumen = f"{pcts[0]}%–{pcts[-1]}% dcto." if pcts[0]!=pcts[-1] else f"{pcts[0]}% dcto."
        elif amts:
            resumen = f"{amts[0]}–{amts[-1]} de dcto." if len(amts)>1 else f"{amts[0]} de dcto."
        else:
            resumen = texts[0][:120]
        out.append({
            "Proveedor":"Movistar - Club Movistar",
            "Categoría":"Promos/Descuentos",
            "Comercio": b,
            "Beneficio": resumen,
            "Vigencia": "",
            "Link": "https://ww2.movistar.cl/app/club/",
            "Fuente": "https://ww2.movistar.cl/app/club/",
            "Extraido_En": datetime.now().isoformat()
        })

    uniq = {(r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
