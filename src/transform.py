"""
transform.py  —  Role: Data Engineer + Data Scientist
-------------------------------------------------------
Pivots the refined long-format table into a wide business-ready view
and computes a composite Economic Health Score per country per year.

Score methodology (equal-weighted, 0–100):
  gdp_per_capita      : higher is better  → normalised to [0,1]
  inflation           : lower is better   → penalty for deviation from 2% target
  unemployment        : lower is better   → normalised inverted
  current_account_pct : closer to 0 is better → moderate surplus/deficit OK
  govt_debt_pct       : lower is better   → normalised inverted (capped at 150%)

DataOps layer : BUSINESS READY
"""

import sqlite3
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timezone
from config.settings import INDICATORS, DB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TRANSFORM] %(message)s")
log = logging.getLogger(__name__)

SCORE_YEAR_MIN = 2005   # Only score years where enough data exists


def init_business_ready_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS economic_health_scores (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code         TEXT    NOT NULL,
            country_name         TEXT    NOT NULL,
            year                 INTEGER NOT NULL,
            gdp_per_capita       REAL,
            inflation            REAL,
            unemployment         REAL,
            current_account_pct  REAL,
            govt_debt_pct        REAL,
            gdp_score            REAL,
            inflation_score      REAL,
            unemployment_score   REAL,
            curr_acc_score       REAL,
            debt_score           REAL,
            health_score         REAL,
            health_tier          TEXT,
            indicators_available INTEGER,
            transformed_at       TEXT    NOT NULL,
            UNIQUE(country_code, year)
        )
    """)
    conn.commit()


def load_refined_wide(conn: sqlite3.Connection) -> pd.DataFrame:
    """Pivot refined_indicators from long to wide format."""
    df = pd.read_sql(
        "SELECT country_code, country_name, indicator, year, value_refined "
        "FROM refined_indicators",
        conn
    )
    wide = df.pivot_table(
        index=["country_code", "country_name", "year"],
        columns="indicator",
        values="value_refined"
    ).reset_index()
    wide.columns.name = None

    # Ensure all indicator columns exist even if missing from data
    for col in INDICATORS.keys():
        if col not in wide.columns:
            wide[col] = np.nan

    return wide


# ── Scoring functions ──────────────────────────────────────────────────────

def score_gdp(series: pd.Series) -> pd.Series:
    """Normalise GDP per capita log-scale to 0–1 (higher = better)."""
    log_vals = np.log1p(series.clip(lower=0))
    lo, hi = log_vals.min(), log_vals.max()
    if hi == lo:
        return pd.Series(0.5, index=series.index)
    return (log_vals - lo) / (hi - lo)


def score_inflation(series: pd.Series) -> pd.Series:
    """
    Inflation score: 1.0 at 2% (central bank target), declines away from it.
    Penalty is steeper for high inflation than for mild deflation.
    """
    target = 2.0
    deviation = (series - target).abs()
    score = 1.0 / (1.0 + deviation / 5.0)   # sigmoid-like decay
    return score.clip(0, 1)


def score_unemployment(series: pd.Series) -> pd.Series:
    """Lower unemployment → higher score. 0% → 1.0, 25%+ → 0.0."""
    return (1.0 - (series.clip(0, 25) / 25.0)).clip(0, 1)


def score_current_account(series: pd.Series) -> pd.Series:
    """
    Current account: moderate surplus/deficit is fine.
    Score peaks at 0%, falls off for large imbalances (±10% GDP).
    """
    return (1.0 - (series.abs().clip(0, 15) / 15.0)).clip(0, 1)


def score_govt_debt(series: pd.Series) -> pd.Series:
    """Lower debt → higher score. 0% → 1.0, 150%+ GDP → 0.0."""
    return (1.0 - (series.clip(0, 150) / 150.0)).clip(0, 1)


def assign_tier(score: float) -> str:
    """Map composite score (0–100) to a qualitative tier."""
    if pd.isna(score):
        return "N/A"
    if score >= 70:
        return "Strong"
    if score >= 50:
        return "Moderate"
    if score >= 30:
        return "Weak"
    return "Fragile"


def compute_scores(wide: pd.DataFrame) -> pd.DataFrame:
    """Add individual and composite health scores to the wide dataframe."""
    df = wide.copy()

    df["gdp_score"]        = score_gdp(df["gdp_per_capita"])
    df["inflation_score"]  = score_inflation(df["inflation"])
    df["unemployment_score"] = score_unemployment(df["unemployment"])
    df["curr_acc_score"]   = score_current_account(df["current_account_pct"])
    df["debt_score"]       = score_govt_debt(df["govt_debt_pct"])

    score_cols = ["gdp_score", "inflation_score", "unemployment_score",
                  "curr_acc_score", "debt_score"]
    # Health score is the mean of available sub-scores × 100
    df["health_score"] = df[score_cols].mean(axis=1, skipna=True) * 100
    df["health_score"] = df["health_score"].round(2)
    df["health_tier"]  = df["health_score"].apply(assign_tier)

    indicator_cols = list(INDICATORS.keys())
    df["indicators_available"] = df[indicator_cols].notna().sum(axis=1)

    return df


def run_transform() -> None:
    """Main entry point. Builds the business-ready economic_health_scores table."""
    conn = sqlite3.connect(DB_PATH)
    init_business_ready_table(conn)

    log.info("Loading refined data and computing economic health scores...")
    wide = load_refined_wide(conn)

    if wide.empty:
        log.error("Refined layer is empty — run remediation first.")
        conn.close()
        return

    wide = wide[wide["year"] >= SCORE_YEAR_MIN]
    scored = compute_scores(wide)
    scored["transformed_at"] = datetime.now(timezone.utc).isoformat()

    cols = [
        "country_code", "country_name", "year",
        "gdp_per_capita", "inflation", "unemployment",
        "current_account_pct", "govt_debt_pct",
        "gdp_score", "inflation_score", "unemployment_score",
        "curr_acc_score", "debt_score",
        "health_score", "health_tier", "indicators_available", "transformed_at"
    ]
    scored = scored[[c for c in cols if c in scored.columns]]
    scored.to_sql("economic_health_scores", conn,
                  if_exists="replace", index=False)
    conn.commit()

    log.info("Transformation complete. %d country-year rows written.", len(scored))

    # Quick summary
    latest = scored[scored["year"] == scored["year"].max()]
    top5 = latest.nlargest(5, "health_score")[["country_name", "year", "health_score", "health_tier"]]
    log.info("Top 5 by health score in %d:\n%s", int(latest["year"].max()), top5.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    run_transform()
