"""
quality_rules.py  —  Role: Data Quality Analyst
-------------------------------------------------
Defines all data quality rules for each CDE, tagged by Gartner
quality dimension. Rules are reusable, composable, and return
structured QualityResult objects that feed into the assess stage.

DataOps phase : DEFINE  (agreeing what "good" looks like)
"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


# ── Result container ───────────────────────────────────────────────────────

@dataclass
class QualityResult:
    """Structured outcome of a single quality rule execution."""
    cde:            str           # e.g. "gdp_per_capita"
    rule_name:      str           # e.g. "completeness_check"
    dimension:      str           # Gartner dimension: completeness, accuracy, etc.
    country_code:   Optional[str] # None = cross-country aggregate
    year_range:     tuple         # (start_year, end_year)
    passed:         bool
    score:          float         # 0.0 – 1.0
    threshold:      float         # agreed minimum acceptable score
    exceptions:     int           # number of failing records
    total_records:  int
    detail:         str           # human-readable explanation
    severity:       str = "medium"  # low / medium / high / critical

    def __post_init__(self):
        # Ensure passed is always a Python bool, not numpy.bool_
        self.passed = bool(self.passed)
        self.score  = float(self.score)
        self.exceptions   = int(self.exceptions)
        self.total_records = int(self.total_records)


# ── Rule implementations ───────────────────────────────────────────────────

class DataQualityRules:
    """
    Encapsulates all quality rules for the economics pipeline CDEs.
    Each method receives a filtered DataFrame (one indicator) and returns
    a list of QualityResult objects — one per country or one aggregate.
    """

    def __init__(self, thresholds: dict):
        """
        thresholds : from config.settings.QUALITY_THRESHOLDS
        """
        self.thresholds = thresholds

    # ── COMPLETENESS ────────────────────────────────────────────────────────

    def completeness_by_country(self, df: pd.DataFrame, cde: str) -> list[QualityResult]:
        """
        Dimension : COMPLETENESS
        Rule      : For each country, at least N% of yearly values must be
                    non-null across the configured time range.
        Severity  : high for critical CDEs, medium otherwise.
        """
        threshold = self.thresholds[cde]["completeness_min"]
        results = []

        for country, grp in df.groupby("country_code"):
            total = len(grp)
            non_null = grp["value"].notna().sum()
            score = non_null / total if total > 0 else 0.0
            passed = score >= threshold
            exceptions = total - non_null
            year_min = int(grp["year"].min())
            year_max = int(grp["year"].max())

            results.append(QualityResult(
                cde=cde,
                rule_name="completeness_by_country",
                dimension="completeness",
                country_code=country,
                year_range=(year_min, year_max),
                passed=passed,
                score=round(score, 4),
                threshold=threshold,
                exceptions=int(exceptions),
                total_records=int(total),
                detail=(
                    f"{int(non_null)}/{total} years populated "
                    f"({'PASS' if passed else 'FAIL'} — threshold {threshold:.0%})"
                ),
                severity="high" if not passed and score < 0.5 else "medium",
            ))
        return results

    def completeness_overall(self, df: pd.DataFrame, cde: str) -> QualityResult:
        """
        Dimension : COMPLETENESS
        Rule      : Aggregate completeness across all countries and years.
        """
        threshold = self.thresholds[cde]["completeness_min"]
        total = len(df)
        non_null = df["value"].notna().sum()
        score = non_null / total if total > 0 else 0.0

        return QualityResult(
            cde=cde,
            rule_name="completeness_overall",
            dimension="completeness",
            country_code=None,
            year_range=(int(df["year"].min()), int(df["year"].max())),
            passed=score >= threshold,
            score=round(score, 4),
            threshold=threshold,
            exceptions=int(total - non_null),
            total_records=int(total),
            detail=f"Overall: {int(non_null)}/{total} non-null values ({score:.1%})",
            severity="critical" if score < 0.5 else "medium",
        )

    # ── VALIDITY ─────────────────────────────────────────────────────────────

    def validity_range_check(self, df: pd.DataFrame, cde: str) -> list[QualityResult]:
        """
        Dimension : VALIDITY
        Rule      : Non-null values must fall within the agreed min/max range
                    for the indicator. Values outside are flagged as exceptions.
        """
        lo, hi = self.thresholds[cde]["value_range"]
        results = []

        for country, grp in df.groupby("country_code"):
            non_null = grp["value"].dropna()
            total = len(non_null)
            if total == 0:
                continue
            out_of_range = non_null[(non_null < lo) | (non_null > hi)]
            exceptions = len(out_of_range)
            score = 1.0 - (exceptions / total)
            passed = exceptions == 0

            results.append(QualityResult(
                cde=cde,
                rule_name="validity_range_check",
                dimension="validity",
                country_code=country,
                year_range=(int(grp["year"].min()), int(grp["year"].max())),
                passed=passed,
                score=round(score, 4),
                threshold=1.0,
                exceptions=exceptions,
                total_records=int(total),
                detail=(
                    f"{exceptions} value(s) outside [{lo}, {hi}]. "
                    + (f"Offenders: {out_of_range.values.tolist()}" if exceptions else "All in range.")
                ),
                severity="high" if exceptions > 0 else "low",
            ))
        return results

    # ── UNIQUENESS ───────────────────────────────────────────────────────────

    def uniqueness_check(self, df: pd.DataFrame, cde: str) -> QualityResult:
        """
        Dimension : UNIQUENESS
        Rule      : Each (country_code, indicator, year) combination must
                    appear exactly once. Duplicates are critical errors.
        """
        total = len(df)
        dupes = df.duplicated(subset=["country_code", "indicator", "year"]).sum()
        score = 1.0 - (dupes / total) if total > 0 else 1.0

        return QualityResult(
            cde=cde,
            rule_name="uniqueness_check",
            dimension="uniqueness",
            country_code=None,
            year_range=(int(df["year"].min()), int(df["year"].max())),
            passed=dupes == 0,
            score=round(score, 4),
            threshold=1.0,
            exceptions=int(dupes),
            total_records=int(total),
            detail=f"{int(dupes)} duplicate (country, indicator, year) keys found.",
            severity="critical" if dupes > 0 else "low",
        )

    # ── CONSISTENCY ──────────────────────────────────────────────────────────

    def consistency_yoy_change(self, df: pd.DataFrame, cde: str) -> list[QualityResult]:
        """
        Dimension : CONSISTENCY
        Rule      : Year-over-year change must not exceed an extreme threshold.
        For economic indicators, a >500% single-year change is a signal of
        data entry error or a unit change — not genuine economic movement.
        (Exception: inflation in hyperinflationary economies is expected to spike.)
        """
        EXTREME_CHANGE_PCT = 500.0
        results = []

        for country, grp in df.groupby("country_code"):
            grp_sorted = grp.sort_values("year").reset_index(drop=True)
            grp_sorted["prev_year"] = grp_sorted["year"].shift(1)
            grp_sorted["prev_value"] = grp_sorted["value"].shift(1)
            grp_sorted["year_gap"] = grp_sorted["year"] - grp_sorted["prev_year"]
            consecutive = grp_sorted[
                grp_sorted["year_gap"].eq(1)
                & grp_sorted["value"].notna()
                & grp_sorted["prev_value"].notna()
            ].copy()

            if consecutive.empty:
                continue

            consecutive["pct_change"] = (
                (consecutive["value"] - consecutive["prev_value"]).abs()
                / consecutive["prev_value"].abs()
            ) * 100
            extreme = consecutive["pct_change"][consecutive["pct_change"] > EXTREME_CHANGE_PCT]
            exceptions = len(extreme)
            total = len(consecutive["pct_change"].dropna())
            score = 1.0 - (exceptions / total) if total > 0 else 1.0

            results.append(QualityResult(
                cde=cde,
                rule_name="consistency_yoy_change",
                dimension="consistency",
                country_code=country,
                year_range=(int(grp["year"].min()), int(grp["year"].max())),
                passed=exceptions == 0,
                score=round(score, 4),
                threshold=1.0,
                exceptions=exceptions,
                total_records=int(total),
                detail=(
                    f"{exceptions} year(s) with >500% YoY change detected "
                    f"(possible data anomaly)."
                ),
                severity="medium" if exceptions > 0 else "low",
            ))
        return results

    # ── TIMELINESS ──────────────────────────────────────────────────────────

    def timeliness_check(self, df: pd.DataFrame, cde: str,
                         expected_latest_year: Optional[int] = None) -> QualityResult:
        """
        Dimension : TIMELINESS
        Rule      : At least 80% of countries should have data for the
                    expected latest year. Missing recent data suggests
                    the source is stale.
        """
        if expected_latest_year is None:
            expected_latest_year = int(df["year"].max())

        n_countries = df["country_code"].nunique()
        recent = df[df["year"] == expected_latest_year]
        recent_with_value = recent[recent["value"].notna()]["country_code"].nunique()
        score = recent_with_value / n_countries if n_countries > 0 else 0.0
        threshold = 0.80

        return QualityResult(
            cde=cde,
            rule_name="timeliness_check",
            dimension="timeliness",
            country_code=None,
            year_range=(expected_latest_year, expected_latest_year),
            passed=score >= threshold,
            score=round(score, 4),
            threshold=threshold,
            exceptions=int(n_countries - recent_with_value),
            total_records=int(n_countries),
            detail=(
                f"{recent_with_value}/{n_countries} countries have {expected_latest_year} data. "
                f"({'PASS' if score >= threshold else 'FAIL'})"
            ),
            severity="medium" if score < threshold else "low",
        )

    # ── RUN ALL ─────────────────────────────────────────────────────────────

    def run_all(
        self,
        df: pd.DataFrame,
        cde: str,
        expected_latest_year: Optional[int] = None,
    ) -> list[QualityResult]:
        """Execute all applicable rules for a CDE and return all results."""
        results = []
        results += self.completeness_by_country(df, cde)
        results.append(self.completeness_overall(df, cde))
        results += self.validity_range_check(df, cde)
        results.append(self.uniqueness_check(df, cde))
        results += self.consistency_yoy_change(df, cde)
        results.append(self.timeliness_check(df, cde, expected_latest_year))
        return results
