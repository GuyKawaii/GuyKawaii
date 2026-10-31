"""Capture deterministic colored ASCII portrait frames from an offline HTML canvas."""
import base64
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image


def portrait_frames(avatar_url):
    from playwright.sync_api import sync_playwright

    response = requests.get(avatar_url, timeout=(15, 60))
    response.raise_for_status()
    # Decode and resize before sending to the browser, with no external requests.
    with Image.open(BytesIO(response.content)) as avatar:
        avatar = avatar.convert('RGB')
        avatar.thumbnail((512, 512))
        buffer = BytesIO()
        avatar.save(buffer, format='PNG')
    source = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')
    html = Path(__file__).resolve().parent.parent / 'assets/ascii-portrait.html'
    frames = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': 600, 'height': 650}, device_scale_factor=1)
            page.goto(html.as_uri())
            page.evaluate('source => window.loadPortrait(source)', source)
            for index in range(16):
                page.evaluate('time => window.drawPortrait(time)', index / 4)
                png = page.locator('#portrait').screenshot(animations='disabled')
                with Image.open(BytesIO(png)) as frame:
                    frames.append(frame.convert('RGB'))
        finally:
            browser.close()
    return frames
