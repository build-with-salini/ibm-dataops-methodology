"""
test_quality_rules.py
---------------------
Unit tests for the DataQualityRules engine.
Each test builds a minimal synthetic DataFrame and asserts
the expected rule outcome — pass/fail, score, exception count.

Run:
    pytest tests/ -v
"""

import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.quality_rules import DataQualityRules

# ── Shared fixture ─────────────────────────────────────────────────────────

THRESHOLDS = {
    "gdp_per_capita": {
        "completeness_min": 0.80,
        "value_range": (100, 200_000),
    },
    "inflation": {
        "completeness_min": 0.75,
        "value_range": (-10, 100),
    },
}


def make_df(country_codes, years, values, indicator="gdp_per_capita") -> pd.DataFrame:
    """Build a minimal test DataFrame."""
    rows = []
    for cc, yr, val in zip(country_codes, years, values):
        rows.append({
            "country_code": cc,
            "country_name": cc,
            "indicator": indicator,
            "year": yr,
            "value": val,
        })
    return pd.DataFrame(rows)


rules = DataQualityRules(THRESHOLDS)


# ══════════════════════════════════════════════════════════════════════════
# COMPLETENESS TESTS
# ══════════════════════════════════════════════════════════════════════════

class TestCompleteness:

    def test_full_completeness_passes(self):
        df = make_df(
            ["US"] * 5, range(2000, 2005),
            [10000, 11000, 12000, 13000, 14000]
        )
        results = rules.completeness_by_country(df, "gdp_per_capita")
        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].score == 1.0
        assert results[0].exceptions == 0

    def test_zero_completeness_fails(self):
        df = make_df(["US"] * 5, range(2000, 2005), [None] * 5)
        results = rules.completeness_by_country(df, "gdp_per_capita")
        assert results[0].passed is False
        assert results[0].score == 0.0
        assert results[0].exceptions == 5

    def test_below_threshold_fails(self):
        # 3 of 5 non-null = 60%, threshold = 80%
        df = make_df(["US"] * 5, range(2000, 2005),
                     [10000, None, 12000, None, 14000])
        results = rules.completeness_by_country(df, "gdp_per_capita")
        assert results[0].passed is False
        assert abs(results[0].score - 0.6) < 0.01

    def test_exactly_at_threshold_passes(self):
        # 4 of 5 = 80%, threshold = 80%
        df = make_df(["US"] * 5, range(2000, 2005),
                     [10000, None, 12000, 13000, 14000])
        results = rules.completeness_by_country(df, "gdp_per_capita")
        assert results[0].passed is True
        assert abs(results[0].score - 0.8) < 0.01

    def test_multiple_countries_independent(self):
        df = make_df(
            ["US", "US", "US", "DE", "DE", "DE", "DE", "DE"],
            [2000, 2001, 2002, 2000, 2001, 2002, 2003, 2004],
            [10000, None, None, 30000, 31000, 32000, 33000, 34000]
        )
        results = {r.country_code: r
                   for r in rules.completeness_by_country(df, "gdp_per_capita")}
        assert results["US"].passed is False   # 33% < 80%
        assert results["DE"].passed is True    # 100% ≥ 80%


# ══════════════════════════════════════════════════════════════════════════
# VALIDITY TESTS
# ══════════════════════════════════════════════════════════════════════════

class TestValidity:

    def test_all_in_range_passes(self):
        df = make_df(["US"] * 3, [2000, 2001, 2002], [1000, 5000, 50000])
        results = rules.validity_range_check(df, "gdp_per_capita")
        assert all(r.passed for r in results)
        assert all(r.exceptions == 0 for r in results)

    def test_value_below_range_flagged(self):
        df = make_df(["US"] * 3, [2000, 2001, 2002], [50, 5000, 50000])
        results = rules.validity_range_check(df, "gdp_per_capita")
        assert results[0].passed is False
        assert results[0].exceptions == 1

    def test_value_above_range_flagged(self):
        df = make_df(["US"] * 3, [2000, 2001, 2002], [1000, 5000, 999_999])
        results = rules.validity_range_check(df, "gdp_per_capita")
        assert results[0].passed is False
        assert results[0].exceptions == 1

    def test_nulls_excluded_from_range_check(self):
        # Null values should not count as out-of-range
        df = make_df(["US"] * 3, [2000, 2001, 2002], [1000, None, 50000])
        results = rules.validity_range_check(df, "gdp_per_capita")
        assert results[0].passed is True
        assert results[0].exceptions == 0

    def test_inflation_negative_allowed(self):
        df = make_df(["JP"] * 3, [2000, 2001, 2002], [-1, 0.5, 2.0],
                     indicator="inflation")
        results = rules.validity_range_check(df, "inflation")
        assert all(r.passed for r in results)

    def test_inflation_hyperinflation_flagged(self):
        # 500% inflation exceeds the 100% upper bound
        df = make_df(["VE"] * 3, [2000, 2001, 2002], [2.0, 50.0, 500.0],
                     indicator="inflation")
        results = rules.validity_range_check(df, "inflation")
        assert results[0].exceptions == 1


# ══════════════════════════════════════════════════════════════════════════
# UNIQUENESS TESTS
# ══════════════════════════════════════════════════════════════════════════

class TestUniqueness:

    def test_no_duplicates_passes(self):
        df = make_df(["US", "US", "DE"], [2000, 2001, 2000], [100, 200, 300])
        result = rules.uniqueness_check(df, "gdp_per_capita")
        assert result.passed is True
        assert result.exceptions == 0
        assert result.score == 1.0

    def test_duplicate_row_fails(self):
        df = make_df(["US", "US", "US"], [2000, 2000, 2001], [100, 110, 200])
        result = rules.uniqueness_check(df, "gdp_per_capita")
        assert result.passed is False
        assert result.exceptions == 1
        assert result.severity == "critical"


# ══════════════════════════════════════════════════════════════════════════
# CONSISTENCY TESTS
# ══════════════════════════════════════════════════════════════════════════

class TestConsistency:

    def test_normal_growth_passes(self):
        # ~5% annual growth — well within 500% threshold
        df = make_df(["US"] * 5, range(2000, 2005),
                     [40000, 42000, 44000, 46000, 48000])
        results = rules.consistency_yoy_change(df, "gdp_per_capita")
        assert all(r.passed for r in results)

    def test_extreme_spike_flagged(self):
        # 1000% jump between 2001 and 2002
        df = make_df(["US"] * 4, [2000, 2001, 2002, 2003],
                     [1000, 1050, 11000, 11500])
        results = rules.consistency_yoy_change(df, "gdp_per_capita")
        assert any(r.exceptions > 0 for r in results)


# ══════════════════════════════════════════════════════════════════════════
# TIMELINESS TESTS
# ══════════════════════════════════════════════════════════════════════════

class TestTimeliness:

    def test_all_countries_have_recent_data_passes(self):
        countries = ["US", "DE", "JP", "CN", "IN", "BR", "FR", "AU",
                     "CA", "IT", "KR", "MX", "RU", "SA", "ZA",
                     "TR", "AR", "ID", "GB"]
        df = make_df(
            countries + countries,
            [2022] * len(countries) + [2021] * len(countries),
            [10000] * len(countries) * 2
        )
        result = rules.timeliness_check(df, "gdp_per_capita", expected_latest_year=2022)
        assert result.passed is True

    def test_missing_recent_data_fails(self):
        # Only 1 of 5 countries has 2022 data
        countries = ["US", "DE", "JP", "CN", "IN"]
        years = [2022, 2020, 2019, 2018, 2017]
        df = make_df(countries, years, [10000] * 5)
        result = rules.timeliness_check(df, "gdp_per_capita", expected_latest_year=2022)
        assert result.passed is False
        assert result.score < 0.80
