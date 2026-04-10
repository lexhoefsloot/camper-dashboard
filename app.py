"""Camper Dashboard — Flask web app for browsing scraped Marktplaats campers."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__)

DB_PATH = os.environ.get("CAMPER_DB", str(Path(__file__).parent / "data" / "campers.db"))


# ── Database helpers ───────────────────────────────────────────────────────────


def get_db():
    """Return a new database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_schema(conn: sqlite3.Connection):
    """Create tables and add missing columns if needed."""
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

        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camper_id INTEGER NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (camper_id) REFERENCES campers(id) ON DELETE CASCADE
        );
    """)

    # Add columns if they don't exist (idempotent migration)
    existing = {row[1] for row in conn.execute("PRAGMA table_info(campers)").fetchall()}
    migrations = {
        "image_urls": "ALTER TABLE campers ADD COLUMN image_urls TEXT",
        "parsed_data": "ALTER TABLE campers ADD COLUMN parsed_data TEXT",
    }
    for col, sql in migrations.items():
        if col not in existing:
            conn.execute(sql)

    conn.commit()


# Run schema migration on startup
with get_db() as _conn:
    ensure_schema(_conn)


# ── Helpers ────────────────────────────────────────────────────────────────────


def camper_to_dict(row: sqlite3.Row) -> dict:
    """Convert a Row to dict, parsing JSON fields."""
    d = dict(row)
    for json_field in ("parsed_data", "image_urls"):
        val = d.get(json_field)
        if val and isinstance(val, str):
            try:
                d[json_field] = json.loads(val)
            except json.JSONDecodeError:
                pass
    # Price from cents to euros
    if d.get("price") is not None:
        d["price_euros"] = d["price"] / 100
    return d


def build_filter_query(params: dict) -> tuple[str, list]:
    """Build WHERE clause from request params. Returns (clause, values)."""
    conditions = []
    values = []

    # Text search
    if q := params.get("q", "").strip():
        conditions.append("(c.title LIKE ? OR c.location LIKE ?)")
        values.extend([f"%{q}%", f"%{q}%"])

    # Price range
    if min_price := params.get("min_price"):
        try:
            conditions.append("c.price >= ?")
            values.append(int(float(min_price) * 100))
        except ValueError:
            pass
    if max_price := params.get("max_price"):
        try:
            conditions.append("c.price <= ?")
            values.append(int(float(max_price) * 100))
        except ValueError:
            pass

    # Parsed data JSON filters (use json_extract)
    json_filters = {
        # Range filters
        "min_bouwjaar": ("json_extract(c.parsed_data, '$.basis.bouwjaar')", ">=", int),
        "max_bouwjaar": ("json_extract(c.parsed_data, '$.basis.bouwjaar')", "<=", int),
        "min_km": ("json_extract(c.parsed_data, '$.basis.kilometerstand')", ">=", int),
        "max_km": ("json_extract(c.parsed_data, '$.basis.kilometerstand')", "<=", int),
        "min_slaapplaatsen": ("json_extract(c.parsed_data, '$.capaciteit.slaapplaatsen')", ">=", int),
        "min_zitplaatsen": ("json_extract(c.parsed_data, '$.capaciteit.zitplaatsen')", ">=", int),
        "min_lengte": ("json_extract(c.parsed_data, '$.technisch.lengte_cm')", ">=", int),
        "max_lengte": ("json_extract(c.parsed_data, '$.technisch.lengte_cm')", "<=", int),
    }

    for param_name, (expr, op, cast) in json_filters.items():
        if val := params.get(param_name):
            try:
                conditions.append(f"CAST({expr} AS INTEGER) {op} ?")
                values.append(cast(val))
            except (ValueError, TypeError):
                pass

    # Dropdown/select filters
    if merk := params.get("merk", "").strip():
        conditions.append("json_extract(c.parsed_data, '$.basis.merk') = ? COLLATE NOCASE")
        values.append(merk)

    if brandstof := params.get("brandstof", "").strip():
        conditions.append("json_extract(c.parsed_data, '$.technisch.brandstof') = ? COLLATE NOCASE")
        values.append(brandstof)

    if transmissie := params.get("transmissie", "").strip():
        conditions.append("json_extract(c.parsed_data, '$.technisch.transmissie') = ? COLLATE NOCASE")
        values.append(transmissie)

    # Boolean toggle filters
    boolean_toggles = {
        "airco": "$.comfort.airco",
        "gps": "$.comfort.GPS",
        "parkeersensoren": "$.comfort.parkeersensoren",
        "keuken": "$.camper.keuken",
        "koelkast": "$.camper.koelkast",
        "douche": "$.camper.douche",
        "toilet": "$.camper.toilet",
        "apk_geldig": "$.onderhoud.APK_geldig",
        "service_historie": "$.onderhoud.service_historie",
    }

    for param_name, json_path in boolean_toggles.items():
        if params.get(param_name) == "1":
            conditions.append(f"json_extract(c.parsed_data, '{json_path}') = 1")

    # Favorites only
    if params.get("favorites") == "1":
        conditions.append("f.id IS NOT NULL")

    where = " AND ".join(conditions) if conditions else "1=1"
    return where, values


# ── Routes ─────────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/camper/<int:camper_id>")
def camper_detail(camper_id: int):
    """Detail page for a single camper."""
    return render_template("detail.html", camper_id=camper_id)


@app.route("/compare")
def compare_page():
    """Comparison page for 2-3 campers."""
    return render_template("compare.html")


# ── API routes ─────────────────────────────────────────────────────────────────


@app.route("/api/campers")
def api_campers():
    """List campers with filtering, sorting, and pagination."""
    params = request.args.to_dict()

    where, values = build_filter_query(params)

    # Sorting
    sort_options = {
        "price_asc": "c.price ASC",
        "price_desc": "c.price DESC",
        "newest": "c.scraped_at DESC",
        "oldest": "c.scraped_at ASC",
        "year_desc": "CAST(json_extract(c.parsed_data, '$.basis.bouwjaar') AS INTEGER) DESC",
        "year_asc": "CAST(json_extract(c.parsed_data, '$.basis.bouwjaar') AS INTEGER) ASC",
        "km_asc": "CAST(json_extract(c.parsed_data, '$.basis.kilometerstand') AS INTEGER) ASC",
    }
    sort = sort_options.get(params.get("sort", ""), "c.price ASC")

    # Pagination
    try:
        page = max(1, int(params.get("page", 1)))
    except ValueError:
        page = 1
    per_page = 24
    offset = (page - 1) * per_page

    conn = get_db()
    try:
        # Count
        count_sql = f"""
            SELECT COUNT(*) FROM campers c
            LEFT JOIN favorites f ON f.camper_id = c.id
            WHERE {where}
        """
        total = conn.execute(count_sql, values).fetchone()[0]

        # Fetch
        sql = f"""
            SELECT c.*, CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
            FROM campers c
            LEFT JOIN favorites f ON f.camper_id = c.id
            WHERE {where}
            ORDER BY {sort}
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(sql, values + [per_page, offset]).fetchall()

        campers = [camper_to_dict(r) for r in rows]

        return jsonify({
            "campers": campers,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        })
    finally:
        conn.close()


@app.route("/api/campers/<int:camper_id>")
def api_camper_detail(camper_id: int):
    """Get single camper with all data."""
    conn = get_db()
    try:
        row = conn.execute("""
            SELECT c.*, CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite
            FROM campers c
            LEFT JOIN favorites f ON f.camper_id = c.id
            WHERE c.id = ?
        """, [camper_id]).fetchone()

        if not row:
            return jsonify({"error": "Camper not found"}), 404

        return jsonify(camper_to_dict(row))
    finally:
        conn.close()


@app.route("/api/campers/<int:camper_id>/favorite", methods=["POST", "DELETE"])
def api_toggle_favorite(camper_id: int):
    """Add or remove a camper from favorites."""
    conn = get_db()
    try:
        if request.method == "POST":
            conn.execute(
                "INSERT OR IGNORE INTO favorites (camper_id) VALUES (?)",
                [camper_id],
            )
            conn.commit()
            return jsonify({"status": "added"})
        else:
            conn.execute("DELETE FROM favorites WHERE camper_id = ?", [camper_id])
            conn.commit()
            return jsonify({"status": "removed"})
    finally:
        conn.close()


@app.route("/api/stats")
def api_stats():
    """Dashboard statistics."""
    conn = get_db()
    try:
        stats = {}
        stats["total"] = conn.execute("SELECT COUNT(*) FROM campers").fetchone()[0]
        stats["favorites"] = conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]

        row = conn.execute(
            "SELECT MIN(price), MAX(price), AVG(price) FROM campers WHERE price > 0"
        ).fetchone()
        if row[0] is not None:
            stats["min_price"] = row[0] / 100
            stats["max_price"] = row[1] / 100
            stats["avg_price"] = round(row[2] / 100)

        stats["last_update"] = conn.execute(
            "SELECT MAX(scraped_at) FROM campers"
        ).fetchone()[0]

        # Unique merken for dropdown
        merken = conn.execute("""
            SELECT DISTINCT json_extract(parsed_data, '$.basis.merk') AS merk
            FROM campers
            WHERE merk IS NOT NULL AND merk != ''
            ORDER BY merk
        """).fetchall()
        stats["merken"] = [r[0] for r in merken if r[0]]

        # Brandstoffen
        brandstoffen = conn.execute("""
            SELECT DISTINCT json_extract(parsed_data, '$.technisch.brandstof') AS brandstof
            FROM campers
            WHERE brandstof IS NOT NULL AND brandstof != ''
            ORDER BY brandstof
        """).fetchall()
        stats["brandstoffen"] = [r[0] for r in brandstoffen if r[0]]

        return jsonify(stats)
    finally:
        conn.close()


@app.route("/api/filter-options")
def api_filter_options():
    """Get available filter values from the data."""
    conn = get_db()
    try:
        result = {}

        # Price range
        row = conn.execute("SELECT MIN(price), MAX(price) FROM campers WHERE price > 0").fetchone()
        result["price_range"] = {"min": (row[0] or 0) / 100, "max": (row[1] or 0) / 100}

        # Year range
        row = conn.execute("""
            SELECT MIN(CAST(json_extract(parsed_data, '$.basis.bouwjaar') AS INTEGER)),
                   MAX(CAST(json_extract(parsed_data, '$.basis.bouwjaar') AS INTEGER))
            FROM campers
            WHERE json_extract(parsed_data, '$.basis.bouwjaar') IS NOT NULL
        """).fetchone()
        result["year_range"] = {"min": row[0] or 1990, "max": row[1] or 2026}

        # KM range
        row = conn.execute("""
            SELECT MIN(CAST(json_extract(parsed_data, '$.basis.kilometerstand') AS INTEGER)),
                   MAX(CAST(json_extract(parsed_data, '$.basis.kilometerstand') AS INTEGER))
            FROM campers
            WHERE json_extract(parsed_data, '$.basis.kilometerstand') IS NOT NULL
              AND json_extract(parsed_data, '$.basis.kilometerstand') > 0
        """).fetchone()
        result["km_range"] = {"min": row[0] or 0, "max": row[1] or 500000}

        return jsonify(result)
    finally:
        conn.close()


@app.route("/api/export/csv")
def api_export_csv():
    """Export all (filtered) campers as CSV."""
    import csv
    import io

    params = request.args.to_dict()
    where, values = build_filter_query(params)

    conn = get_db()
    try:
        rows = conn.execute(f"""
            SELECT c.* FROM campers c
            LEFT JOIN favorites f ON f.camper_id = c.id
            WHERE {where}
            ORDER BY c.price ASC
        """, values).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        headers = [
            "ID", "Marktplaats ID", "Titel", "Prijs (€)", "Locatie", "URL",
            "Merk", "Model", "Bouwjaar", "Kilometerstand", "Brandstof",
            "Transmissie", "Vermogen PK", "Lengte cm",
            "Slaapplaatsen", "Zitplaatsen",
            "Airco", "GPS", "Parkeersensoren",
            "Keuken", "Koelkast", "Douche", "Toilet",
            "APK Geldig", "Service Historie",
            "Scraped At",
        ]
        writer.writerow(headers)

        for row in rows:
            d = camper_to_dict(row)
            pd = d.get("parsed_data") or {}
            basis = pd.get("basis", {})
            tech = pd.get("technisch", {})
            cap = pd.get("capaciteit", {})
            comfort = pd.get("comfort", {})
            camper = pd.get("camper", {})
            onderhoud = pd.get("onderhoud", {})

            writer.writerow([
                d.get("id"),
                d.get("marktplaats_id"),
                d.get("title"),
                d.get("price_euros"),
                d.get("location"),
                d.get("url"),
                basis.get("merk"),
                basis.get("model"),
                basis.get("bouwjaar"),
                basis.get("kilometerstand"),
                tech.get("brandstof"),
                tech.get("transmissie"),
                tech.get("vermogen_PK"),
                tech.get("lengte_cm"),
                cap.get("slaapplaatsen"),
                cap.get("zitplaatsen"),
                "Ja" if comfort.get("airco") else "Nee",
                "Ja" if comfort.get("GPS") else "Nee",
                "Ja" if comfort.get("parkeersensoren") else "Nee",
                "Ja" if camper.get("keuken") else "Nee",
                "Ja" if camper.get("koelkast") else "Nee",
                "Ja" if camper.get("douche") else "Nee",
                "Ja" if camper.get("toilet") else "Nee",
                "Ja" if onderhoud.get("APK_geldig") else "Nee",
                "Ja" if onderhoud.get("service_historie") else "Nee",
                d.get("scraped_at"),
            ])

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=campers.csv"},
        )
    finally:
        conn.close()


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
