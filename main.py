import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from scrapers.entel import parse_entel, URL as ENTEL_URL
from scrapers.movistar import parse_movistar, URL as MOV_URL
from scrapers.bci import parse_bci, URL as BCI_URL
from scrapers.caja18 import parse_all as parse_caja18, URLS as CAJA18_URLS

# NUEVOS:
from scrapers.bancochile import parse_all as parse_bch, URLS as BCH_URLS
from scrapers.bancoestado import parse_all as parse_be, URLS as BE_URLS

from sheets import write_rows

async def fetch(page, url):
    await page.goto(url, wait_until="networkidle")
    return await page.content()

async def run():
    rows = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Entel (público)
        entel_html = await fetch(page, ENTEL_URL)
        rows += parse_entel(entel_html)

        # Movistar (página pública del Club)
        mov_html = await fetch(page, MOV_URL)
        rows += parse_movistar(mov_html)

        # Bci Beneficios (público)
        bci_html = await fetch(page, BCI_URL)
        rows += parse_bci(bci_html)

        # Caja 18 (múltiples URLs)
        html_map_caja18 = {}
        for u in CAJA18_URLS:
            html_map_caja18[u] = await fetch(page, u)
        rows += parse_caja18(html_map_caja18)

        # Banco de Chile (múltiples URLs)
        html_map_bch = {}
        for u in BCH_URLS:
            html_map_bch[u] = await fetch(page, u)
        rows += parse_bch(html_map_bch)

        # BancoEstado (múltiples URLs)
        html_map_be = {}
        for u in BE_URLS:
            html_map_be[u] = await fetch(page, u)
        rows += parse_be(html_map_be)

        await browser.close()

    # Deduplicación global por Proveedor+Comercio+Beneficio
    uniq = {(r["Proveedor"], r["Comercio"], r["Beneficio"]): r for r in rows}
    rows = list(uniq.values())

    write_rows(rows)
    print(f"[{datetime.now().isoformat()}] Filas escritas: {len(rows)}")

if __name__ == "__main__":
    asyncio.run(run())
