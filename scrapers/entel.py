from bs4 import BeautifulSoup
from datetime import datetime
from scrapers.utils import looks_like_offer

URL = "https://www.entel.cl/beneficios"

BRANDS = [
    "Castaño","Starbucks","Just Burger","Burger King","Dunkin","Mr. Pretzels","Boost",
    "Papa Johns","Cinemark","miCoca-Cola","Torre","Bata","North Star","Bubble Gummers"
]

def pick_brand(title, text):
    blob = f"{title} {text}".lower()
    for b in BRANDS:
        if b.lower().replace(" ", "") in blob.replace(" ", ""):
            return b
    return (title or text[:40]).strip()

def parse_entel(html: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for el in soup.find_all(["section","div","article","li","a"]):
        text = el.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue
        title_tag = el.find(["h3","h2","strong","b"])
        title = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]
        brand = pick_brand(title, text)
        out.append({
            "Proveedor":"Entel - Club Entel",
            "Categoría":"Beneficios",
            "Comercio": brand,
            "Beneficio": text,
            "Vigencia":"",
            "Link": URL,
            "Fuente": URL,
            "Extraido_En": datetime.now().isoformat()
        })
    uniq = {(r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
