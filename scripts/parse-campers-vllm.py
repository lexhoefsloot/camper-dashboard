#!/usr/bin/env python3
"""
Parse camper descriptions using VLLM (Qwen 3.5 27B).
Extracts structured data from raw descriptions.
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any

# Config
VLLM_URL = "http://192.168.1.135:8000/v1/chat/completions"
VLLM_MODEL = "Qwen3.5-27B"
VLLM_API_KEY = "dummy"
RAW_FILE = Path(__file__).parent.parent / "data" / "campers_raw.json"
DB_PATH = Path(__file__).parent.parent / "data" / "campers.db"

# System prompt for structured extraction
SYSTEM_PROMPT = """
You are a data extraction assistant for camper advertisements.
Extract structured information from the description and return ONLY valid JSON.

Return this exact JSON structure (all fields in Dutch):
{
  "basis": {
    "merk": string or null,
    "model": string or null,
    "bouwjaar": number or null,
    "kilometerstand": number or null,
    "kenteken": string or null
  },
  "capaciteit": {
    "slaapplaatsen": number or null,
    "zitplaatsen": number or null,
    "vaste_bedden": number or null,
    "opklap_bedden": number or null
  },
  "technisch": {
    "brandstof": string or null,
    "transmissie": string or null,
    "vermogen_PK": number or null,
    "lengte_cm": number or null
  },
  "comfort": {
    "airco": boolean,
    "GPS": boolean,
    "parkeersensoren": boolean
  },
  "camper": {
    "keuken": boolean,
    "koelkast": boolean,
    "douche": boolean,
    "toilet": boolean
  },
  "onderhoud": {
    "APK_geldig": boolean,
    "service_historie": boolean
  }
}

Rules:
- Use null for missing/unknown values
- Use true/false for booleans (default false if not mentioned)
- Numbers: extract digits only (e.g., "2015" not "2015 jaar")
- Kilometers: extract number, remove "km"
- Length: convert to cm (e.g., "7.2m" → 720)
- Be strict: only extract what is explicitly mentioned
- Return ONLY JSON, no markdown, no explanations
"""

USER_PROMPT_TEMPLATE = """
Extract structured data from this camper advertisement:

Title: {title}
Description: {description}

Return the JSON structure as defined in the system prompt.
"""


async def parse_with_vllm(title: str, description: str) -> dict[str, Any] | None:
    """Send description to VLLM and parse response."""
    import httpx

    user_prompt = USER_PROMPT_TEMPLATE.format(
        title=title or "",
        description=description[:4000] if description else "",  # Truncate to avoid token limits
    )

    payload = {
        "model": VLLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,  # Low for consistency
        "max_tokens": 1024,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                VLLM_URL,
                json=payload,
                headers={"Authorization": f"Bearer {VLLM_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Clean up markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            content = content.strip()

            return json.loads(content)

    except Exception as e:
        print(f"  ⚠️ Parse error: {e}")
        return None


def ensure_db(conn: sqlite3.Connection) -> None:
    """Create tables and ensure schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS campers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marktplaats_id TEXT UNIQUE,
            title TEXT,
            price INTEGER,
            location TEXT,
            url TEXT,
            raw_html TEXT,
            image_urls TEXT,
            parsed_data TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Add columns if missing
    existing = {row[1] for row in conn.execute("PRAGMA table_info(campers)").fetchall()}
    migrations = {
        "image_urls": "ALTER TABLE campers ADD COLUMN image_urls TEXT",
        "parsed_data": "ALTER TABLE campers ADD COLUMN parsed_data TEXT",
    }
    for col, sql in migrations.items():
        if col not in existing:
            conn.execute(sql)

    conn.commit()


async def parse_one(item: dict[str, Any]) -> dict[str, Any]:
    """Parse a single camper item."""
    title = item.get("title", "")
    description = item.get("description", "")

    print(f"  Parsing: {title[:50]}...")

    parsed = await parse_with_vllm(title, description)

    if parsed:
        item["parsed_data"] = parsed
        print(f"  ✅ Parsed successfully")
    else:
        print(f"  ❌ Failed to parse")

    return item


async def main():
    """Main entry point."""
    # Load raw data
    if not RAW_FILE.exists():
        print(f"❌ Raw file not found: {RAW_FILE}")
        print("Run marktplaats-camper-scraper.py first")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"[parser] Loaded {len(items)} campers to parse")

    # Ensure database exists
    conn = sqlite3.connect(DB_PATH)
    ensure_db(conn)
    conn.commit()

    # Parse each item
    success_count = 0
    for item in items:
        parsed_item = await parse_one(item)

        # Insert into database
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO campers
                (marktplaats_id, title, price, location, url, raw_html, image_urls, parsed_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    parsed_item.get("marktplaats_id"),
                    parsed_item.get("title"),
                    parsed_item.get("price"),
                    parsed_item.get("location"),
                    parsed_item.get("url"),
                    parsed_item.get("description"),
                    json.dumps(parsed_item.get("image_urls", [])),
                    json.dumps(parsed_item.get("parsed_data"), ensure_ascii=False) if parsed_item.get("parsed_data") else None,
                ),
            )
            conn.commit()
            success_count += 1
        except Exception as e:
            print(f"  ❌ DB error: {e}")

    conn.close()

    print(f"\n✅ Parsed {success_count}/{len(items)} campers")
    print(f"📁 Database: {DB_PATH}")
    print("\nNext: Start the dashboard with 'python app.py'")


if __name__ == "__main__":
    asyncio.run(main())
