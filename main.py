import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PwTimeoutError

# Scrapers (asegúrate de que estos módulos expongan estas constantes/funciones)
from scrapers.entel import parse_entel, URL as ENTEL_URL
from scrapers.movistar import parse_movistar, URLS as MOV_URLS
from scrapers.bci import parse_bci, URL as BCI_URL
from scrapers.caja18 import parse_all as parse_caja18, URLS as CAJA18_URLS
from scrapers.bancochile import parse_all as parse_bch, URLS as BCH_URLS
from scrapers.bancoestado import parse_all as parse_be, URLS as BE_URLS

# Escritura a Google Sheets
from sheets import write_rows

# Normalizador (convierte texto crudo en Marca/Descuento/Días/Categoría normalizada/Link corto)
from normalizer import normalize_row


async def accept_cookies_if_any(page):
    """
    Intenta aceptar banners de cookies/consentimiento comunes.
    No falla si no encuentra nada.
    """
    selectors = [
        "text=Aceptar", "text=Aceptar todo", "text=Acepto", "text=Estoy de acuerdo",
        "button:has-text('Aceptar')", "button:has-text('Aceptar todo')",
        "[aria-label*='Aceptar']", "[id*='accept']", "[class*='accept']",
        "text=Entendido", "button:has-text('Entendido')"
    ]
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if el:
                await el.click()
                await page.wait_for_timeout(500)
        except Exception:
            # Ignorar errores de click/timeout en consent
            pass


async def gentle_load(page, url: str) -> str:
    """
    Visita una URL, espera a que la página esté ociosa, intenta aceptar cookies,
    hace un scroll suave para gatillar contenido lazy y devuelve el HTML.
    """
    try:
        await page.goto(url, wait_until="networkidle", timeout=45000)
        await page.wait_for_selector("body", timeout=10000)
        # banner de cookies / consent si existe
        await accept_cookies_if_any(page)
        # Scroll suave para cargar contenido perezoso (cards, imágenes)
        for _ in range(4):
            await page.mouse.wheel(0, 2200)
            await page.wait_for_timeout(400)
        html = await page.content()
        return html
    except PwTimeoutError:
        print(f"[WARN] Timeout cargando: {url}")
        return ""
    except Exception as e:
        print(f"[WARN] Error cargando {url}: {e}")
        return ""


async def run():
    rows = []

    async with async_playwright() as p:
        # Lanzar Chromium
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox"]
        )
        # User-Agent “normal” para evitar servir variantes excesivamente minimalistas
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123 Safari/537.36"
            )
        )

        # =============== ENTEL ===============
        entel_html = await gentle_load(page, ENTEL_URL)
        entel_rows = parse_entel(entel_html) if entel_html else []
        print(f"[INFO] ENTEL items: {len(entel_rows)}")
        rows += entel_rows

        # =============== MOVISTAR (múltiples URLs) ===============
        mov_rows_total = []
        for u in MOV_URLS:
            mov_html = await gentle_load(page, u)
            part = parse_movistar(mov_html) if mov_html else []
            print(f"[INFO] MOVISTAR {u} items: {len(part)}")
            mov_rows_total += part
        rows += mov_rows_total

        # =============== BCI ===============
        bci_html = await gentle_load(page, BCI_URL)
        bci_rows = parse_bci(bci_html) if bci_html else []
        print(f"[INFO] BCI items: {len(bci_rows)}")
        rows += bci_rows

        # =============== CAJA 18 (múltiples URLs) ===============
        html_map_caja18 = {}
        for u in CAJA18_URLS:
            h = await gentle_load(page, u)
            if h:
                html_map_caja18[u] = h
        caja_rows = parse_caja18(html_map_caja18) if html_map_caja18 else []
        print(f"[INFO] CAJA18 items: {len(caja_rows)}")
        rows += caja_rows

        # =============== BANCO DE CHILE (múltiples URLs) ===============
        html_map_bch = {}
        for u in BCH_URLS:
            h = await gentle_load(page, u)
            if h:
                html_map_bch[u] = h
        bch_rows = parse_bch(html_map_bch) if html_map_bch else []
        print(f"[INFO] BANCO DE CHILE items: {len(bch_rows)}")
        rows += bch_rows

        # =============== BANCOESTADO (múltiples URLs) ===============
        html_map_be = {}
        for u in BE_URLS:
            h = await gentle_load(page, u)
            if h:
                html_map_be[u] = h
        be_rows = parse_be(html_map_be) if html_map_be else []
        print(f"[INFO] BANCOESTADO items: {len(be_rows)}")
        rows += be_rows

        await browser.close()

    # ====== Deduplicación global por Proveedor + Comercio + Beneficio ======
    before = len(rows)
    uniq = {(r.get("Proveedor",""), r.get("Comercio",""), r.get("Beneficio","")): r for r in rows}
    rows = list(uniq.values())
    print(f"[INFO] Dedup: {before} -> {len(rows)}")

    # ====== Normalización (Marca, Descuento, Días, Categoría normalizada, Link corto) ======
    rows = [normalize_row(r) for r in rows]

    # ====== Escritura a Google Sheets ======
    print(f"[INFO] Total filas a escribir: {len(rows)}")
    write_rows(rows)
    print(f"[{datetime.now().isoformat()}] OK")


if __name__ == "__main__":
    asyncio.run(run())
