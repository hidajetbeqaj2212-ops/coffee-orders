#!/usr/bin/env python3
"""Renders tools/brand/brand.html into the XBar wordmark (embedded as LOGO in prototype/pos.html) and the app icons.
Needs: pip install playwright pillow && playwright install chromium. Then: python3 tools/brand/render.py && npm run build:ui"""
import asyncio, base64, io, pathlib, re
from PIL import Image
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(device_scale_factor=2)
        await pg.goto((ROOT / 'tools/brand/brand.html').as_uri()); await pg.wait_for_timeout(400)
        mark = await pg.locator('#mark').screenshot(omit_background=True)
        icon = await pg.locator('#icon').screenshot(omit_background=True)
        await b.close()
    im = Image.open(io.BytesIO(mark)); im = im.crop(im.getbbox())
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    uri = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    im.save(ROOT / 'app/icons/wordmark.png', optimize=True)
    src = ROOT / 'prototype/pos.html'; s = src.read_text()
    s, n = re.subn(r"const LOGO='data:image/png;base64,[^']*';", lambda m: f"const LOGO='{uri}';", s); assert n == 1
    src.write_text(s)
    ic = Image.open(io.BytesIO(icon)).convert('RGBA').resize((512, 512), Image.LANCZOS)
    ic.save(ROOT / 'build/icon.png')
    flat = Image.new('RGB', ic.size, '#111111'); flat.paste(ic, mask=ic.split()[3])
    flat.save(ROOT / 'app/icons/icon-512.png'); flat.resize((192, 192), Image.LANCZOS).save(ROOT / 'app/icons/icon-192.png')
    print('logo', im.size, 'icons written')
asyncio.run(main())
