"""
assess.py  —  Role: Data Quality Analyst
------------------------------------------
Loads raw data from SQLite, runs all quality rules per CDE,
and persists results to quality_scores and quality_exceptions tables.

DataOps phase : ASSESS  (measure actual quality vs. defined thresholds)
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime, timezone
from config.settings import INDICATORS, DB_PATH, QUALITY_THRESHOLDS, END_YEAR
from src.quality_rules import DataQualityRules, QualityResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ASSESS] %(message)s")
log = logging.getLogger(__name__)


def init_quality_tables(conn: sqlite3.Connection) -> None:
    """Create quality result tables if they don't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quality_scores (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            assessed_at   TEXT    NOT NULL,
            cde           TEXT    NOT NULL,
            rule_name     TEXT    NOT NULL,
            dimension     TEXT    NOT NULL,
            country_code  TEXT,
            year_from     INTEGER,
            year_to       INTEGER,
            passed        INTEGER NOT NULL,
            score         REAL    NOT NULL,
            threshold     REAL    NOT NULL,
            exceptions    INTEGER NOT NULL,
            total_records INTEGER NOT NULL,
            detail        TEXT,
            severity      TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quality_summary (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            assessed_at     TEXT    NOT NULL,
            cde             TEXT    NOT NULL,
            overall_score   REAL    NOT NULL,
            rules_passed    INTEGER NOT NULL,
            rules_failed    INTEGER NOT NULL,
            total_exceptions INTEGER NOT NULL,
            status          TEXT    NOT NULL
        )
    """)
    conn.commit()


def load_raw_for_cde(conn: sqlite3.Connection, cde: str) -> pd.DataFrame:
    """Load all raw rows for a given CDE name from raw_indicators."""
    return pd.read_sql(
        "SELECT * FROM raw_indicators WHERE indicator = ?",
        conn, params=(cde,)
    )


def persist_results(conn: sqlite3.Connection, results: list[QualityResult],
                    assessed_at: str) -> None:
    """Write quality rule results to quality_scores table."""
    rows = [{
        "assessed_at":   assessed_at,
        "cde":           r.cde,
        "rule_name":     r.rule_name,
        "dimension":     r.dimension,
        "country_code":  r.country_code,
        "year_from":     r.year_range[0],
        "year_to":       r.year_range[1],
        "passed":        int(r.passed),
        "score":         r.score,
        "threshold":     r.threshold,
        "exceptions":    r.exceptions,
        "total_records": r.total_records,
        "detail":        r.detail,
        "severity":      r.severity,
    } for r in results]

    pd.DataFrame(rows).to_sql("quality_scores", conn,
                              if_exists="append", index=False)
    conn.commit()


def persist_summary(conn: sqlite3.Connection, cde: str,
                    results: list[QualityResult], assessed_at: str) -> dict:
    """Compute and write a summary row for the CDE."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    total_ex = sum(r.exceptions for r in results)
    scores = [r.score for r in results]
    overall = round(sum(scores) / len(scores), 4) if scores else 0.0
    status = "PASS" if failed == 0 else ("WARN" if overall >= 0.70 else "FAIL")

    conn.execute("""
        INSERT INTO quality_summary
            (assessed_at, cde, overall_score, rules_passed, rules_failed,
             total_exceptions, status)
        VALUES (?,?,?,?,?,?,?)
    """, (assessed_at, cde, overall, passed, failed, total_ex, status))
    conn.commit()

    log.info("  %-25s  overall=%.1f%%  rules=%d passed / %d failed  status=%s",
             cde, overall * 100, passed, failed, status)
    return {"cde": cde, "overall_score": overall, "status": status}


def run_assessment() -> list[dict]:
    """
    Main entry point.
    Runs all quality rules for every CDE and returns a list of summary dicts.
    """
    conn = sqlite3.connect(DB_PATH)
    init_quality_tables(conn)
    rules = DataQualityRules(QUALITY_THRESHOLDS)
    assessed_at = datetime.now(timezone.utc).isoformat()
    summaries = []

    log.info("Starting data quality assessment for %d CDEs", len(INDICATORS))

    for cde in INDICATORS:
        log.info("Assessing CDE: %s", cde)
        df = load_raw_for_cde(conn, cde)

        if df.empty:
            log.warning("  No raw data found for %s — skipping.", cde)
            continue

        results = rules.run_all(df, cde, expected_latest_year=END_YEAR)
        persist_results(conn, results, assessed_at)
        summary = persist_summary(conn, cde, results, assessed_at)
        summaries.append(summary)

    conn.close()
    log.info("Assessment complete.")
    return summaries


if __name__ == "__main__":
    summaries = run_assessment()
    for s in summaries:
        print(f"  {s['cde']:<28} {s['overall_score']:.1%}  [{s['status']}]")
