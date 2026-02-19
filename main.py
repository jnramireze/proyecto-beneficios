import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from scrapers.entel import parse_entel, URL as ENTEL_URL
from scrapers.movistar import parse_movistar, URL as MOV_URL
from scrapers.bci import parse_bci, URL as BCI_URL
from scrapers.caja18 import parse_all as parse_caja18, URLS as CAJA18_URLS
from sheets import write_rows

async def fetch(page, url):
    await page.goto(url, wait_until="networkidle")
    return await page.content()

async def run():
    rows = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Entel
        entel_html = await fetch(page, ENTEL_URL)
        rows += parse_entel(entel_html)

        # Movistar
        mov_html = await fetch(page, MOV_URL)
        rows += parse_movistar(mov_html)

        # Bci
        bci_html = await fetch(page, BCI_URL)
        rows += parse_bci(bci_html)

        # Caja 18 (múltiples fuentes)
        html_map = {}
        for u in CAJA18_URLS:
            html_map[u] = await fetch(page, u)
        rows += parse_caja18(html_map)

        await browser.close()

    # Deduplicar por Proveedor+Comercio+Beneficio
    uniq = {}
    for r in rows:
        key = (r["Proveedor"], r["Comercio"], r["Beneficio"])
        uniq[key] = r
    rows = list(uniq.values())

    write_rows(rows)
    print(f"[{datetime.now().isoformat()}] Filas escritas: {len(rows)}")

if __name__ == "__main__":
    asyncio.run(run())

