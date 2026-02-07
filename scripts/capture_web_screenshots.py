#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from pathlib import Path


async def main() -> int:
    output = Path("artifacts/screenshots_web")
    output.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        print(f"SKIPPED: playwright not installed ({exc})")
        print("Install steps: pip install playwright && python -m playwright install chromium")
        return 0

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        await page.screenshot(path=str(output / "01_hero_home.png"), full_page=True)

        await page.keyboard.press("Control+K")
        await page.screenshot(path=str(output / "02_command_palette.png"), full_page=True)

        await page.click("button:has-text('Session Memory')")
        await page.screenshot(path=str(output / "03_memory_panel.png"), full_page=True)

        await browser.close()

    print(f"Saved web screenshots to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
