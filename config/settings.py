"""
settings.py
-----------
Central configuration for the DataOps Economics Pipeline.
All indicator codes, country lists, time ranges, and quality
thresholds are defined here so they can be changed in one place.
"""

# ── World Bank indicator codes ─────────────────────────────────────────────
INDICATORS = {
    "gdp_per_capita":        "NY.GDP.PCAP.CD",   # GDP per capita (current USD)
    "inflation":             "FP.CPI.TOTL.ZG",   # Inflation, consumer prices (annual %)
    "unemployment":          "SL.UEM.TOTL.ZS",   # Unemployment (% of total labour force)
    "current_account_pct":   "BN.CAB.XOKA.GD.ZS",# Current account balance (% of GDP)
    "govt_debt_pct":         "GC.DOD.TOTL.GD.ZS",# Central govt debt (% of GDP)
}

# ── G20 countries (ISO 3166-1 alpha-2) ────────────────────────────────────
G20_COUNTRIES = {
    "AR": "Argentina",
    "AU": "Australia",
    "BR": "Brazil",
    "CA": "Canada",
    "CN": "China",
    "FR": "France",
    "DE": "Germany",
    "IN": "India",
    "ID": "Indonesia",
    "IT": "Italy",
    "JP": "Japan",
    "MX": "Mexico",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "ZA": "South Africa",
    "KR": "South Korea",
    "TR": "Turkey",
    "GB": "United Kingdom",
    "US": "United States",
}

# ── Time range ─────────────────────────────────────────────────────────────
START_YEAR = 2000
END_YEAR   = 2023

# Latest year expected by timeliness checks and dashboard copy.
LATEST_DATA_YEAR = END_YEAR

# ── World Bank API ─────────────────────────────────────────────────────────
WB_API_BASE  = "https://api.worldbank.org/v2"
WB_PAGE_SIZE = 1000

# ── SQLite database path ───────────────────────────────────────────────────
DB_PATH = "data/economics.db"

# ── Data quality thresholds (agreed with 'business') ──────────────────────
# Keys match the INDICATORS dict above.
# completeness_min = minimum % of non-null values required to pass
# value_range      = (min, max) inclusive — values outside are flagged
QUALITY_THRESHOLDS = {
    "gdp_per_capita": {
        "completeness_min": 0.80,
        "value_range": (100, 200_000),
    },
    "inflation": {
        "completeness_min": 0.75,
        "value_range": (-10, 100),
    },
    "unemployment": {
        "completeness_min": 0.75,
        "value_range": (0, 50),
    },
    "current_account_pct": {
        "completeness_min": 0.70,
        "value_range": (-30, 30),
    },
    "govt_debt_pct": {
        "completeness_min": 0.65,
        "value_range": (0, 300),
    },
}

# ── Reporting ──────────────────────────────────────────────────────────────
QUALITY_REPORT_PATH = "reports/quality_report.html"
CATALOG_PATH        = "catalog/data_catalog.yml"
CDE_DEFS_PATH       = "catalog/cde_definitions.yml"
