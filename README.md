# DataOps Economics Pipeline

A **production-style DataOps project** that applies IBM's DataOps Methodology to open macroeconomic data — ingesting World Bank indicators for all G20 nations, running a structured data quality framework, maintaining a live data catalog, and delivering an interactive Streamlit dashboard.

Built as a portfolio project to demonstrate end-to-end DataOps engineering skills.

---

## What This Project Demonstrates

| Concept | Implementation |
|---------|---------------|
| **IBM DataOps Methodology** | Full Establish → Iterate → Improve cycle in code |
| **Data Quality Framework** | Define → Assess → Remediate → Monitor per CDE |
| **Gartner Quality Dimensions** | Rules tagged by dimension: completeness, validity, uniqueness, consistency, timeliness |
| **Critical Data Elements (CDEs)** | 5 CDEs defined with business names, owners, thresholds, lineage |
| **Data Catalog & Metadata** | Live YAML + SQLite catalog with quality scores, lineage, and governance metadata |
| **Three-Layer Architecture** | Raw → Refined → Business Ready data layers in SQLite |
| **DataOps Orchestration** | Roles assigned per pipeline stage (Data Engineer, Quality Analyst, Data Steward) |
| **Sprint-based delivery** | Resumable pipeline with stage-level checkpointing |
| **Python + SQL** | pandas, SQLite, Plotly, Streamlit |
| **Testing** | 17 pytest unit tests for all quality rule logic |

---

## Architecture

```
World Bank API
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│  INGEST  (Data Engineer)                                │
│  • Fetches 5 indicators × 19 G20 countries × 23 years   │
│  • Writes raw, unmodified observations to SQLite        │
│  • Preserves nulls — no silent transformation           │
└───────────────────────┬─────────────────────────────────┘
                        │ raw_indicators
                        ▼
┌─────────────────────────────────────────────────────────┐
│  ASSESS  (Data Quality Analyst)                         │
│  • Runs quality rules per CDE per country               │
│  • Dimensions: completeness, validity, uniqueness,      │
│    consistency, timeliness                              │
│  • Writes scores + exceptions to quality_scores        │
└───────────────────────┬─────────────────────────────────┘
                        │ quality_scores / quality_summary
                        ▼
┌─────────────────────────────────────────────────────────┐
│  REMEDIATE  (Data Engineer + Quality Analyst)           │
│  • Deduplicates records                                 │
│  • Nulls out-of-range values (does not silently fix)    │
│  • Interpolates short gaps (≤2 consecutive years)       │
│  • Logs every change to remediation_log                 │
└───────────────────────┬─────────────────────────────────┘
                        │ refined_indicators
                        ▼
┌─────────────────────────────────────────────────────────┐
│  TRANSFORM  (Data Engineer + Data Scientist)            │
│  • Pivots long → wide format                            │
│  • Computes composite Economic Health Score (0–100)     │
│  • Assigns health tier: Strong / Moderate / Weak /      │
│    Fragile                                              │
└───────────────────────┬─────────────────────────────────┘
                        │ economic_health_scores
                        ▼
┌─────────────────────────────────────────────────────────┐
│  CATALOG  (Data Steward)                                │
│  • Merges CDE definitions with live quality scores      │
│  • Publishes to YAML + SQLite catalog                   │
│  • Records lineage, ownership, thresholds, freshness    │
└───────────────────────┬─────────────────────────────────┘
                        │ data_catalog
                        ▼
               Streamlit Dashboard
     (Pipeline / Quality / Economics / Catalog)
```

---

## Project Structure

```
dataops-economics-pipeline/
│
├── config/
│   └── settings.py              # Indicators, countries, thresholds, paths
│
├── catalog/
│   ├── cde_definitions.yml      # CDE metadata: owners, lineage, dimensions
│   └── data_catalog.yml         # Generated: live catalog with quality scores
│
├── src/
│   ├── ingest.py                # World Bank API → raw_indicators (Data Engineer)
│   ├── quality_rules.py         # All quality rules, tagged by Gartner dimension
│   ├── assess.py                # Runs rules, writes quality_scores (DQ Analyst)
│   ├── remediate.py             # Cleanses data → refined_indicators
│   ├── transform.py             # Builds economic_health_scores (business ready)
│   └── catalog_manager.py       # Builds and publishes data catalog (Data Steward)
│
├── pipeline/
│   └── run_pipeline.py          # Orchestrator: runs all stages end-to-end
│
├── dashboard/
│   └── app.py                   # Streamlit: 4-tab interactive dashboard
│
├── tests/
│   └── test_quality_rules.py    # 17 pytest unit tests for quality rules
│
├── data/
│   └── economics.db             # SQLite database (gitignored, generated)
│
├── Makefile                     # make install / run / test / dashboard
└── requirements.txt
```

---

## Database Schema

All data is stored in a local SQLite database (`data/economics.db`) with clear layer separation:

| Table | Layer | Description |
|-------|-------|-------------|
| `raw_indicators` | Raw | Source data as ingested — nulls preserved, no transforms |
| `quality_scores` | Quality | Per-rule results: dimension, score, exceptions, severity |
| `quality_summary` | Quality | Aggregate CDE scores and pass/fail status per run |
| `remediation_log` | Quality | Audit trail of every change made during remediation |
| `refined_indicators` | Refined | Deduplicated, range-validated, gap-interpolated data |
| `economic_health_scores` | Business Ready | Wide-format pivoted table with composite health scores |
| `data_catalog` | Catalog | Live CDE metadata enriched with quality and freshness |
| `ingest_log` | Ops | Timestamp, row counts, and status per ingestion run |

---

## Data Quality Framework

Each CDE goes through a four-stage quality lifecycle:

### 1. Define
Quality requirements are specified in `catalog/cde_definitions.yml` and `config/settings.py` before any measurement begins. For each CDE:
- Relevant Gartner quality **dimensions** are selected (e.g. completeness, validity, timeliness)
- Acceptable **thresholds** are defined (e.g. ≥80% completeness, values within expected range)
- These thresholds are treated as **business agreements** — not technical defaults

### 2. Assess
`src/quality_rules.py` implements five rule categories:

| Rule | Dimension | What it checks |
|------|-----------|---------------|
| `completeness_by_country` | Completeness | ≥N% non-null values per country per CDE |
| `completeness_overall` | Completeness | Aggregate non-null rate across all countries |
| `validity_range_check` | Validity | Values fall within the agreed min/max range |
| `uniqueness_check` | Uniqueness | No duplicate (country, indicator, year) keys |
| `consistency_yoy_change` | Consistency | No >500% year-over-year changes (anomaly signal) |
| `timeliness_check` | Timeliness | ≥80% of countries have data for the most recent year |

### 3. Remediate
`src/remediate.py` applies targeted fixes with full audit logging:
- **Duplicates** → deduplicated, keeping most recent ingestion
- **Out-of-range values** → nulled and logged (not silently corrected)
- **Short gaps** → linearly interpolated if ≤2 consecutive missing years
- All changes written to `remediation_log` with original value, resolved value, and action taken

### 4. Monitor
The Streamlit dashboard's **Data Quality tab** provides ongoing monitoring:
- Completeness heatmap by country × indicator
- Quality score trends across assessment runs
- Filterable exception log by CDE, dimension, severity

---

## Critical Data Elements (CDEs)

| CDE | Business Name | Domain | Critical | Completeness Target |
|-----|--------------|--------|----------|-------------------|
| `gdp_per_capita` | GDP Per Capita (USD) | Macroeconomic Output | ✅ | ≥80% |
| `inflation` | Inflation Rate (Annual %) | Monetary Stability | ✅ | ≥75% |
| `unemployment` | Unemployment Rate (%) | Labour Market | ✅ | ≥75% |
| `current_account_pct` | Current Account Balance (% GDP) | External Balance | — | ≥70% |
| `govt_debt_pct` | Government Debt (% GDP) | Fiscal Position | — | ≥65% |

All CDEs are defined with full lineage (source → raw → refined → business ready), ownership, privacy classification, and quality dimension assignments in `catalog/cde_definitions.yml`.

---

## Economic Health Score

The business-ready layer computes a composite **Economic Health Score** (0–100) per country per year, aggregating five normalised sub-scores:

| Sub-score | Method |
|-----------|--------|
| GDP score | Log-normalised to [0,1] — higher GDP → higher score |
| Inflation score | Peaks at 2% target, decays symmetrically |
| Unemployment score | 0% → 1.0, 25%+ → 0.0 linear decay |
| Current account score | Peaks at balanced (0%), decays for large imbalances |
| Govt debt score | 0% → 1.0, 150%+ GDP → 0.0 linear decay |

Health tiers: **Strong** (≥70) · **Moderate** (≥50) · **Weak** (≥30) · **Fragile** (<30)

---

## Dashboard

Four tabs, all driven live from SQLite:

**🏠 Pipeline Overview** — Row counts per layer, country completeness bar chart, ingestion log

**🔍 Data Quality** — CDE scorecards, passed/failed rules chart, completeness heatmap, filterable exception table

**📈 Economic Analysis** — Health score time series, latest-year bar rankings, GDP vs unemployment scatter, per-indicator country comparison

**📚 Data Catalog** — Searchable catalog cards with lineage, quality scores, thresholds, and governance metadata per CDE

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/your-username/dataops-economics-pipeline.git
cd dataops-economics-pipeline
pip install -r requirements.txt

# 2. Run the full pipeline (requires internet — pulls World Bank API)
make run

# 3. Launch the dashboard
make dashboard

# 4. Run tests
make test
```

To resume from a specific stage (useful after a failure or code change):
```bash
make run-from s=assess     # re-run from assess onwards
make run-from s=transform  # just redo the scoring layer
```

---

## Data Source

All data is sourced from the **[World Bank World Development Indicators (WDI)](https://databank.worldbank.org/source/world-development-indicators)** — a free, open, and widely cited macroeconomic database covering 200+ countries from 1960 to present.

No API key required. Data is fetched at runtime via the public REST API.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Core language |
| pandas | Data manipulation |
| SQLite / SQLAlchemy | Three-layer data store |
| Streamlit | Interactive dashboard |
| Plotly | Visualisations |
| PyYAML | CDE definitions and catalog |
| pytest | Quality rule unit tests |
| Makefile | One-command developer experience |

---

## Methodology Reference

This project applies the **IBM DataOps Methodology** as taught in the [IBM DataOps Methodology course on Coursera](https://www.coursera.org/learn/ibm-data-ops-methodology), covering:
- The DataOps three-phase lifecycle (Establish → Iterate → Improve)
- The IBM AI Ladder (Collect → Organize → Analyze → Infuse)
- Data quality framework (Define → Assess → Remediate → Monitor)
- Gartner data quality dimensions (objective and subjective)
- Data catalog and metadata management
- CDE identification and sprint-based delivery
- DataOps orchestration and role assignments
