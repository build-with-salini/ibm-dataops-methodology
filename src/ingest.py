"""
ingest.py  —  Role: Data Engineer
----------------------------------
Pulls raw macroeconomic indicators from the World Bank API for all
G20 countries and writes them to the raw_indicators table in SQLite.

DataOps layer : RAW  (no transformations, no cleansing — source truth)
"""

import requests
import pandas as pd
import sqlite3
import logging
from datetime import datetime, timezone
from config.settings import (
    INDICATORS, G20_COUNTRIES, START_YEAR, END_YEAR,
    WB_API_BASE, WB_PAGE_SIZE, DB_PATH
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [INGEST] %(message)s")
log = logging.getLogger(__name__)


def fetch_indicator(indicator_code: str, country_code: str) -> list[dict]:
    """
    Call the World Bank REST API for one indicator / country combination.
    Returns a list of annual observation dicts.
    """
    url = (
        f"{WB_API_BASE}/country/{country_code}/indicator/{indicator_code}"
        f"?format=json&date={START_YEAR}:{END_YEAR}&per_page={WB_PAGE_SIZE}"
    )
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        payload = response.json()
        # World Bank returns [metadata, data]; data is index 1
        if len(payload) < 2 or not payload[1]:
            log.warning("No data returned for %s / %s", indicator_code, country_code)
            return []
        return payload[1]
    except requests.RequestException as e:
        log.error("API error for %s / %s: %s", indicator_code, country_code, e)
        return []


def parse_observations(raw_records: list[dict], indicator_name: str, country_code: str) -> list[dict]:
    """
    Flatten raw World Bank response records into a clean row structure
    for the raw layer. No value transformation — nulls are preserved as-is.
    """
    rows = []
    for rec in raw_records:
        rows.append({
            "country_code":    country_code,
            "country_name":    G20_COUNTRIES.get(country_code, country_code),
            "indicator":       indicator_name,
            "indicator_code":  rec.get("indicator", {}).get("id", ""),
            "year":            int(rec.get("date", 0)),
            "value":           rec.get("value"),          # None preserved intentionally
            "ingested_at":     datetime.now(timezone.utc).isoformat(),
        })
    return rows


def init_db(conn: sqlite3.Connection) -> None:
    """Create the raw_indicators table if it doesn't already exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_indicators (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code   TEXT    NOT NULL,
            country_name   TEXT    NOT NULL,
            indicator      TEXT    NOT NULL,
            indicator_code TEXT    NOT NULL,
            year           INTEGER NOT NULL,
            value          REAL,
            ingested_at    TEXT    NOT NULL,
            UNIQUE(country_code, indicator, year)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ingest_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at       TEXT    NOT NULL,
            rows_written INTEGER NOT NULL,
            status       TEXT    NOT NULL,
            notes        TEXT
        )
    """)
    conn.commit()


def run_ingestion() -> int:
    """
    Main entry point.
    Fetches all indicators for all G20 countries and upserts into raw_indicators.
    Returns total rows written.
    """
    import os
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    all_rows = []
    total_countries = len(G20_COUNTRIES)
    total_indicators = len(INDICATORS)

    log.info("Starting ingestion: %d countries × %d indicators (%d–%d)",
             total_countries, total_indicators, START_YEAR, END_YEAR)

    for idx, (country_code, country_name) in enumerate(G20_COUNTRIES.items(), 1):
        for indicator_name, indicator_code in INDICATORS.items():
            log.info("[%d/%d] %s — %s", idx, total_countries, country_name, indicator_name)
            raw_records = fetch_indicator(indicator_code, country_code)
            rows = parse_observations(raw_records, indicator_name, country_code)
            all_rows.extend(rows)

    if all_rows:
        df = pd.DataFrame(all_rows)
        # Upsert: insert or replace on unique (country_code, indicator, year)
        df.to_sql("raw_indicators", conn, if_exists="append", index=False,
                  method="multi")
        # Remove any accidental duplicates from repeated runs
        conn.execute("""
            DELETE FROM raw_indicators
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM raw_indicators
                GROUP BY country_code, indicator, year
            )
        """)
        conn.commit()

    rows_written = len(all_rows)
    conn.execute(
        "INSERT INTO ingest_log (run_at, rows_written, status, notes) VALUES (?,?,?,?)",
        (datetime.now(timezone.utc).isoformat(), rows_written, "SUCCESS",
         f"{total_countries} countries, {total_indicators} indicators")
    )
    conn.commit()
    conn.close()

    log.info("Ingestion complete. %d rows written to raw_indicators.", rows_written)
    return rows_written


if __name__ == "__main__":
    run_ingestion()
