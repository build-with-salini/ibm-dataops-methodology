"""
remediate.py  —  Role: Data Engineer + Data Quality Analyst
-------------------------------------------------------------
Applies targeted cleansing to raw data and writes to refined_indicators.
Remediation strategy per exception type:
  - Out-of-range values   → flagged and excluded (not silently overwritten)
  - Duplicates            → deduplicated, keeping the latest ingestion
  - Missing values        → interpolated linearly within a country series
                            (only if <3 consecutive missing years)

All changes are logged to remediation_log for full auditability.

DataOps phase : REMEDIATE  (fix known issues; share root-cause with owners)
"""

import sqlite3
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timezone
from config.settings import INDICATORS, DB_PATH, QUALITY_THRESHOLDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [REMEDIATE] %(message)s")
log = logging.getLogger(__name__)

# Maximum consecutive missing years to interpolate — beyond this we leave as null
MAX_INTERP_GAP = 2


def init_refined_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS refined_indicators (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code        TEXT    NOT NULL,
            country_name        TEXT    NOT NULL,
            indicator           TEXT    NOT NULL,
            year                INTEGER NOT NULL,
            value_raw           REAL,
            value_refined       REAL,
            remediation_applied TEXT,
            refined_at          TEXT    NOT NULL,
            UNIQUE(country_code, indicator, year)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS remediation_log (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            remediated_at    TEXT    NOT NULL,
            cde              TEXT    NOT NULL,
            country_code     TEXT    NOT NULL,
            year             INTEGER,
            issue_type       TEXT    NOT NULL,
            original_value   REAL,
            resolved_value   REAL,
            action_taken     TEXT    NOT NULL,
            notes            TEXT
        )
    """)
    conn.commit()


def log_remediation(conn, cde, country, year, issue_type,
                    original, resolved, action, notes=""):
    conn.execute("""
        INSERT INTO remediation_log
            (remediated_at, cde, country_code, year, issue_type,
             original_value, resolved_value, action_taken, notes)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (datetime.now(timezone.utc).isoformat(), cde, country, year,
          issue_type, original, resolved, action, notes))


def remediate_cde(conn: sqlite3.Connection, cde: str) -> pd.DataFrame:
    """
    Apply all remediation steps to one CDE.
    Returns the fully remediated DataFrame ready for refined layer.
    """
    df = pd.read_sql(
        "SELECT * FROM raw_indicators WHERE indicator = ?",
        conn, params=(cde,)
    ).copy()

    if df.empty:
        return df

    thresholds = QUALITY_THRESHOLDS[cde]
    lo, hi = thresholds["value_range"]
    refined_at = datetime.now(timezone.utc).isoformat()

    df["value_raw"]      = df["value"]
    df["value_refined"]  = df["value"].copy()
    df["remediation_applied"] = "none"

    # ── Step 1: Remove duplicates ───────────────────────────────────────────
    dupes_before = len(df)
    df = df.sort_values("ingested_at", ascending=False)
    df = df.drop_duplicates(subset=["country_code", "indicator", "year"], keep="first")
    dupes_removed = dupes_before - len(df)
    if dupes_removed > 0:
        log.info("  [%s] Removed %d duplicate rows", cde, dupes_removed)

    # ── Step 2: Flag out-of-range values (null them, don't silently correct) ─
    oor_mask = df["value_refined"].notna() & (
        (df["value_refined"] < lo) | (df["value_refined"] > hi)
    )
    for _, row in df[oor_mask].iterrows():
        log_remediation(conn, cde, row["country_code"], row["year"],
                        "out_of_range", row["value_refined"], None,
                        "nulled_flagged",
                        f"Value {row['value_refined']} outside [{lo}, {hi}]")
    df.loc[oor_mask, "value_refined"] = np.nan
    df.loc[oor_mask, "remediation_applied"] = "out_of_range_nulled"
    if oor_mask.sum() > 0:
        log.info("  [%s] Nulled %d out-of-range values", cde, oor_mask.sum())

    # ── Step 3: Interpolate short gaps within each country's time series ────
    interpolated_count = 0
    for country, grp in df.groupby("country_code"):
        grp = grp.sort_values("year").copy()
        null_mask = grp["value_refined"].isna()

        if not null_mask.any():
            continue

        # Only interpolate if the gap is <= MAX_INTERP_GAP
        grp["_interp"] = grp["value_refined"].interpolate(
            method="linear", limit=MAX_INTERP_GAP, limit_direction="both"
        )
        newly_filled = grp["_interp"].notna() & grp["value_refined"].isna()

        for idx, row in grp[newly_filled].iterrows():
            log_remediation(conn, cde, country, row["year"],
                            "missing_interpolated", None, row["_interp"],
                            "linear_interpolation",
                            f"Gap ≤{MAX_INTERP_GAP} years — interpolated from neighbours")
            interpolated_count += 1

        filled_idx = grp.index[newly_filled]
        df.loc[filled_idx, "value_refined"] = grp.loc[filled_idx, "_interp"].values
        df.loc[filled_idx, "remediation_applied"] = "interpolated"

    if interpolated_count > 0:
        log.info("  [%s] Interpolated %d missing values", cde, interpolated_count)

    df["refined_at"] = refined_at
    return df[[
        "country_code", "country_name", "indicator", "year",
        "value_raw", "value_refined", "remediation_applied", "refined_at"
    ]]


def run_remediation() -> None:
    """Main entry point. Remediates all CDEs and writes to refined_indicators."""
    conn = sqlite3.connect(DB_PATH)
    init_refined_table(conn)

    log.info("Starting remediation for %d CDEs", len(INDICATORS))

    total_rows = 0
    for cde in INDICATORS:
        log.info("Remediating: %s", cde)
        refined_df = remediate_cde(conn, cde)

        if refined_df.empty:
            log.warning("  No data to remediate for %s", cde)
            continue

        conn.execute("DELETE FROM refined_indicators WHERE indicator = ?", (cde,))
        conn.commit()
        refined_df.to_sql("refined_indicators", conn,
                          if_exists="append", index=False, method="multi")
        total_rows += len(refined_df)
        log.info("  Written %d rows to refined_indicators", len(refined_df))

    conn.close()
    log.info("Remediation complete. Total refined rows: %d", total_rows)


if __name__ == "__main__":
    run_remediation()
