# normalizer.py
import re
from urllib.parse import urlparse

BRAND_MAP = {
    # Gastronomía
    "starbucks":"Gastronomía","dunkin":"Gastronomía","papa john":"Gastronomía",
    "burger king":"Gastronomía","melt":"Gastronomía","castaño":"Gastronomía",
    # Entradas / entretención
    "cinemark":"Entradas/Eventos","cinépolis":"Entradas/Eventos","cineplanet":"Entradas/Eventos","kidzania":"Entradas/Eventos",
    # Salud / belleza
    "ahumada":"Salud y bienestar","examedi":"Salud y bienestar","dental":"Salud y bienestar",
    # Transporte / viajes
    "uber":"Transporte","wetransport":"Transporte","salones vip":"Viajes/Salones VIP","avianca":"Viajes/Salones VIP",
    # Retail / tecnología / mascotas
    "accesorios movistar":"Retail","mercado libre":"Retail","zig-zag":"Retail",
    "club softys":"Hogar","mi coca-cola":"Retail","torre":"Retail","bata":"Retail","north star":"Retail","bubble gummers":"Retail",
}

PCT = re.compile(r"(\\d+%)")
AMT = re.compile(r"(\\$\\s?\\d{1,3}(?:[\\.\\,]\\d{3})*)")
DAYS = re.compile(r"(lunes|martes|mi[eé]rcoles|jueves|viernes|s[áa]bado|domingo|todos los d[ií]as)", re.IGNORECASE)

def _norm_brand(comercio, beneficio):
    base = (comercio or "").lower()
    txt = (beneficio or "").lower()
    for k in sorted(BRAND_MAP.keys(), key=len, reverse=True):
        if k in base or k in txt:
            return k.title(), BRAND_MAP[k]
    # fallback
    return (comercio[:60] if comercio else (beneficio[:60] if beneficio else "Oferta")), "Otros"

def _norm_desc(beneficio):
    # extrae % o $ y arma una frase compacta
    p = PCT.findall(beneficio)
    a = AMT.findall(beneficio)
    d = DAYS.findall(beneficio)
    parts = []
    if p: parts.append(", ".join(p))
    if a: parts.append(", ".join(a))
    desc = ", ".join(parts) if parts else beneficio[:120]
    dias = ", ".join(sorted(set([x.title() for x in d]))) if d else ""
    return desc.strip(), dias

def _host(url):
    try:
        net = urlparse(url).netloc
        return net.replace("www.","")
    except:
        return ""

def normalize_row(row):
    comercio, cat, beneficio, link = row.get("Comercio",""), row.get("Categoría",""), row.get("Beneficio",""), row.get("Link","")
    marca, cat_norm = _norm_brand(comercio, beneficio)
    desc, dias = _norm_desc(beneficio or "")
    link_show = link if (link and link.startswith(("http","https"))) else row.get("Fuente","")
    fuente = _host(link_show)
    return {
        **row,
        "Marca": marca,
        "Categoria_norm": cat_norm,
        "Descuento": desc,
        "Dias": dias,
        "Link_show": link_show,
        "Fuente_corta": fuente or "—"
    }
