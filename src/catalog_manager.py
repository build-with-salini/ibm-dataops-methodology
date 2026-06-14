"""
catalog_manager.py  —  Role: Data Steward
-------------------------------------------
Reads CDE definitions from YAML and enriches them with live quality
scores from the database to produce a full data catalog entry per asset.
The catalog is serialised back to YAML and also stored in SQLite for
dashboard consumption.

DataOps concept : DATA CATALOG & METADATA MANAGEMENT
"""

import sqlite3
import yaml
import json
import pandas as pd
import logging
from datetime import datetime, timezone
from config.settings import DB_PATH, CDE_DEFS_PATH, CATALOG_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s [CATALOG] %(message)s")
log = logging.getLogger(__name__)


def load_cde_definitions(path: str = CDE_DEFS_PATH) -> dict:
    """Load CDE metadata from the YAML definition file."""
    with open(path, "r") as f:
        return yaml.safe_load(f).get("cdes", {})


def get_latest_quality_scores(conn: sqlite3.Connection) -> dict:
    """
    Pull the most recent quality summary per CDE from the database.
    Returns a dict keyed by CDE name.
    """
    df = pd.read_sql("""
        SELECT cde, overall_score, rules_passed, rules_failed,
               total_exceptions, status, assessed_at
        FROM quality_summary
        WHERE assessed_at = (SELECT MAX(assessed_at) FROM quality_summary)
    """, conn)

    return {
        row["cde"]: {
            "overall_score":     round(row["overall_score"] * 100, 1),
            "rules_passed":      int(row["rules_passed"]),
            "rules_failed":      int(row["rules_failed"]),
            "total_exceptions":  int(row["total_exceptions"]),
            "quality_status":    row["status"],
            "last_assessed":     row["assessed_at"],
        }
        for _, row in df.iterrows()
    }


def get_data_freshness(conn: sqlite3.Connection) -> dict:
    """Get the latest year available per CDE from the refined layer."""
    df = pd.read_sql("""
        SELECT indicator,
               MAX(year)    AS latest_year,
               COUNT(*)     AS total_rows,
               SUM(CASE WHEN value_refined IS NOT NULL THEN 1 ELSE 0 END) AS non_null_rows
        FROM refined_indicators
        GROUP BY indicator
    """, conn)
    return {
        row["indicator"]: {
            "latest_year": int(row["latest_year"]),
            "total_rows":  int(row["total_rows"]),
            "non_null_rows": int(row["non_null_rows"]),
        }
        for _, row in df.iterrows()
    }


def build_catalog(conn: sqlite3.Connection) -> list[dict]:
    """
    Merge CDE definitions with live quality scores and freshness info
    to produce full catalog entries.
    """
    cde_defs   = load_cde_definitions()
    quality    = get_latest_quality_scores(conn)
    freshness  = get_data_freshness(conn)
    built_at   = datetime.now(timezone.utc).isoformat()
    entries    = []

    for cde_key, meta in cde_defs.items():
        q = quality.get(cde_key, {})
        f = freshness.get(cde_key, {})

        entry = {
            # ── Identity ──────────────────────────────────────────────
            "asset_id":        f"econ_pipeline.{cde_key}",
            "business_name":   meta.get("business_name", cde_key),
            "technical_name":  cde_key,
            "indicator_code":  meta.get("indicator_code", ""),
            "domain":          meta.get("domain", ""),
            "description":     meta.get("description", "").strip(),
            # ── Ownership & Governance ─────────────────────────────────
            "owner":           meta.get("owner", ""),
            "privacy_class":   meta.get("privacy_class", "Public"),
            "critical_cde":    meta.get("critical", False),
            "quality_dims":    meta.get("quality_dims", []),
            # ── Thresholds ─────────────────────────────────────────────
            "completeness_threshold_pct": int(meta.get("thresholds", {}).get("completeness_min", 0) * 100),
            "value_range":     meta.get("thresholds", {}).get("value_range", []),
            # ── Live Quality Scores ─────────────────────────────────────
            "quality_score_pct":    q.get("overall_score"),
            "quality_status":       q.get("quality_status", "NOT_ASSESSED"),
            "rules_passed":         q.get("rules_passed"),
            "rules_failed":         q.get("rules_failed"),
            "total_exceptions":     q.get("total_exceptions"),
            "last_assessed":        q.get("last_assessed"),
            # ── Freshness ───────────────────────────────────────────────
            "latest_year":          f.get("latest_year"),
            "total_rows":           f.get("total_rows"),
            "non_null_rows":        f.get("non_null_rows"),
            # ── Lineage ─────────────────────────────────────────────────
            "lineage_source":       meta.get("lineage", {}).get("source", ""),
            "lineage_raw":          meta.get("lineage", {}).get("raw", ""),
            "lineage_refined":      meta.get("lineage", {}).get("refined", ""),
            "lineage_business":     meta.get("lineage", {}).get("business_ready", ""),
            # ── Catalog metadata ────────────────────────────────────────
            "catalog_built_at":    built_at,
        }
        entries.append(entry)

    return entries


def persist_catalog(conn: sqlite3.Connection, entries: list[dict]) -> None:
    """Write catalog entries to the catalog table in SQLite."""
    conn.execute("DROP TABLE IF EXISTS data_catalog")
    conn.execute("""
        CREATE TABLE data_catalog (
            asset_id                    TEXT,
            business_name               TEXT,
            technical_name              TEXT,
            indicator_code              TEXT,
            domain                      TEXT,
            description                 TEXT,
            owner                       TEXT,
            privacy_class               TEXT,
            critical_cde                INTEGER,
            quality_dims                TEXT,
            completeness_threshold_pct  INTEGER,
            value_range                 TEXT,
            quality_score_pct           REAL,
            quality_status              TEXT,
            rules_passed                INTEGER,
            rules_failed                INTEGER,
            total_exceptions            INTEGER,
            last_assessed               TEXT,
            latest_year                 INTEGER,
            total_rows                  INTEGER,
            non_null_rows               INTEGER,
            lineage_source              TEXT,
            lineage_raw                 TEXT,
            lineage_refined             TEXT,
            lineage_business            TEXT,
            catalog_built_at            TEXT
        )
    """)
    rows = []
    for e in entries:
        row = dict(e)
        row["quality_dims"] = json.dumps(e.get("quality_dims", []))
        row["value_range"]  = json.dumps(e.get("value_range", []))
        row["critical_cde"] = int(e.get("critical_cde", False))
        rows.append(row)
    pd.DataFrame(rows).to_sql("data_catalog", conn, if_exists="append", index=False)
    conn.commit()


def export_catalog_yaml(entries: list[dict], path: str = CATALOG_PATH) -> None:
    """Serialise the catalog to a human-readable YAML file."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump({"catalog": entries, "generated_at": datetime.now(timezone.utc).isoformat()},
                  f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    log.info("Catalog exported to %s", path)


def run_catalog_build() -> list[dict]:
    """Main entry point. Builds and persists the data catalog."""
    conn = sqlite3.connect(DB_PATH)
    log.info("Building data catalog...")
    entries = build_catalog(conn)
    persist_catalog(conn, entries)
    export_catalog_yaml(entries)
    conn.close()

    log.info("Catalog built with %d asset entries.", len(entries))
    for e in entries:
        score = e.get("quality_score_pct")
        score_str = f"{score:.1f}%" if score is not None else "n/a"
        log.info("  %-30s  quality=%s  status=%s",
                 e["business_name"], score_str, e["quality_status"])
    return entries


if __name__ == "__main__":
    run_catalog_build()
