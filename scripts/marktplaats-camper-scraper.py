#!/usr/bin/env python3
"""
Marktplaats Camper Scraper
Scrapes campers from Marktplaats using Playwright (anti-bot).
"""

import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

# Config
SEARCH_URL = "https://www.marktplaats.nl/z/campers-bussen/5737EL"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "campers_raw.json"
MAX_RESULTS = 50


async def scrape():
    """Scrape campers from Marktplaats."""
    print(f"[scraper] Starting scrape from {SEARCH_URL}...")

    async with async_playwright() as p:
        # Launch browser with anti-bot settings
        browser = await p.chromium.launch(
            headless=False,  # More reliable for anti-bot
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="nl-NL",
        )

        page = await context.new_page()

        # Disable automation detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        try:
            # Navigate to search page
            print("[scraper] Navigating to Marktplaats...")
            await page.goto(SEARCH_URL, wait_until="networkidle", timeout=60000)

            # Wait for results to load
            await page.wait_for_selector('[data-sem="listingItem"]', timeout=30000)
            await asyncio.sleep(2)  # Let everything render

            # Extract __NEXT_DATA__ from page
            next_data = await page.evaluate("""
                () => {
                    const script = document.querySelector('script#__NEXT_DATA__');
                    return script ? JSON.parse(script.textContent) : null;
                }
            """)

            if not next_data:
                print("[scraper] ERROR: Could not find __NEXT_DATA__")
                return []

            # Extract listings from Next.js state
            listings = []
            props = next_data.get("props", {})
            pageProps = props.get("pageProps", {})
            searchResults = pageProps.get("searchResults", {})
            items = searchResults.get("items", [])

            print(f"[scraper] Found {len(items)} items in search results")

            for item in items[:MAX_RESULTS]:
                listing = {
                    "marktplaats_id": item.get("id"),
                    "title": item.get("title"),
                    "price": item.get("price", {}).get("amount", 0),
                    "location": item.get("location", {}).get("city") or item.get("location", {}).get("region"),
                    "url": f"https://www.marktplaats.nl/{item.get('id')}/",
                    "image_urls": [
                        img.get("url")
                        for img in item.get("images", [])
                        if img.get("url")
                    ],
                    "description": item.get("description", ""),
                    "scraped_at": asyncio.get_event_loop().time(),
                }
                listings.append(listing)

            print(f"[scraper] Successfully scraped {len(listings)} campers")

            # Save to file
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(listings, f, indent=2, ensure_ascii=False)

            print(f"[scraper] Saved to {OUTPUT_FILE}")

            return listings

        except Exception as e:
            print(f"[scraper] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []

        finally:
            await browser.close()


async def main():
    """Main entry point."""
    listings = await scrape()

    if listings:
        print(f"\n✅ Scraped {len(listings)} campers")
        print(f"📁 Output: {OUTPUT_FILE}")
        print("\nNext: Run parse-campers-vllm.py to extract structured data")
    else:
        print("\n❌ No campers scraped")


if __name__ == "__main__":
    asyncio.run(main())
