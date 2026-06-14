"""
app.py  —  Streamlit Dashboard
--------------------------------
Four-tab interactive dashboard for the DataOps Economics Pipeline.

  Tab 1 — Pipeline Overview   : data freshness, row counts, last run status
  Tab 2 — Data Quality        : quality scores per CDE, exception heatmap,
                                 dimension breakdown, trend over assessments
  Tab 3 — Economic Analysis   : business-ready charts — health scores, GDP,
                                 inflation, unemployment across G20 nations
  Tab 4 — Data Catalog        : searchable catalog with CDE metadata,
                                 lineage, quality status, and thresholds

Run:
    streamlit run dashboard/app.py
"""

import sqlite3
import json
import sys
from pathlib import Path

# Add parent directory to path so config module can be found
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config.settings import LATEST_DATA_YEAR

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataOps Economics Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "data/economics.db"

# ── Helpers ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_table(table: str) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def db_exists() -> bool:
    return Path(DB_PATH).exists()


def status_badge(status: str) -> str:
    colours = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴",
               "NOT_ASSESSED": "⚪", "Strong": "🟢",
               "Moderate": "🟡", "Weak": "🟠", "Fragile": "🔴"}
    return f"{colours.get(status, '⚪')} {status}"


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 DataOps Economics")
    st.caption("IBM DataOps Methodology · Portfolio Project")
    st.divider()
    st.markdown("""
    **Pipeline layers**
    - 🟦 Raw — World Bank API
    - 🟨 Refined — Cleansed & validated
    - 🟩 Business Ready — Scored & pivoted

    **Quality framework**
    Define → Assess → Remediate → Monitor
    """)
    st.divider()
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Data: World Bank WDI · G20 Nations · 2000–{LATEST_DATA_YEAR}")

# ── Guard: DB must exist ───────────────────────────────────────────────────
if not db_exists():
    st.error("Database not found. Run the pipeline first:")
    st.code("python -m pipeline.run_pipeline", language="bash")
    st.stop()

# ── Load all tables ────────────────────────────────────────────────────────
raw_df       = load_table("raw_indicators")
refined_df   = load_table("refined_indicators")
scores_df    = load_table("economic_health_scores")
quality_df   = load_table("quality_scores")
summary_df   = load_table("quality_summary")
catalog_df   = load_table("data_catalog")
ingest_log   = load_table("ingest_log")

# ══════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Pipeline Overview",
    "🔍 Data Quality",
    "📈 Economic Analysis",
    "📚 Data Catalog",
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — PIPELINE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Pipeline Overview")
    st.caption("End-to-end status of each DataOps layer")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw rows ingested",   f"{len(raw_df):,}"     if not raw_df.empty else "–")
    c2.metric("Refined rows",         f"{len(refined_df):,}" if not refined_df.empty else "–")
    c3.metric("Business-ready rows",  f"{len(scores_df):,}"  if not scores_df.empty else "–")
    c4.metric("CDEs tracked",
              str(raw_df["indicator"].nunique()) if not raw_df.empty else "–")

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Layer Row Counts")
        layer_data = pd.DataFrame({
            "Layer":  ["Raw", "Refined", "Business Ready"],
            "Rows":   [len(raw_df), len(refined_df), len(scores_df)],
            "Colour": ["#1f77b4", "#ff7f0e", "#2ca02c"],
        })
        fig = px.bar(layer_data, x="Layer", y="Rows",
                     color="Layer",
                     color_discrete_map={"Raw": "#1f77b4",
                                         "Refined": "#ff7f0e",
                                         "Business Ready": "#2ca02c"},
                     text="Rows")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Data Coverage by Country")
        if not refined_df.empty:
            coverage = (
                refined_df.groupby("country_code")["value_refined"]
                .agg(lambda x: x.notna().mean())
                .reset_index()
                .rename(columns={"value_refined": "completeness"})
            )
            coverage["completeness_pct"] = (coverage["completeness"] * 100).round(1)
            fig2 = px.bar(
                coverage.sort_values("completeness_pct"),
                x="completeness_pct", y="country_code",
                orientation="h",
                labels={"completeness_pct": "Completeness %", "country_code": "Country"},
                color="completeness_pct",
                color_continuous_scale="RdYlGn",
                range_color=[50, 100],
            )
            fig2.update_layout(height=380, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Ingestion Log")
    if not ingest_log.empty:
        st.dataframe(ingest_log.sort_values("run_at", ascending=False).head(10),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No ingestion runs recorded yet.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Data Quality Framework")
    st.caption("Define → Assess → Remediate → Monitor")

    if summary_df.empty:
        st.warning("No quality assessments found. Run `python -m pipeline.run_pipeline --from assess`")
    else:
        # ── Summary scorecard ──────────────────────────────────────────────
        latest_run = summary_df["assessed_at"].max()
        latest = summary_df[summary_df["assessed_at"] == latest_run].copy()

        st.subheader(f"Latest Assessment — `{latest_run[:19]}`")
        cols = st.columns(len(latest))
        for col, (_, row) in zip(cols, latest.iterrows()):
            col.metric(
                label=row["cde"].replace("_", " ").title(),
                value=f"{row['overall_score']*100:.1f}%",
                delta=status_badge(row["status"]),
            )

        st.divider()
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Quality Score by CDE")
            fig = px.bar(
                latest.sort_values("overall_score"),
                x="overall_score", y="cde",
                orientation="h",
                color="overall_score",
                color_continuous_scale="RdYlGn",
                range_color=[0.5, 1.0],
                labels={"overall_score": "Score (0–1)", "cde": "CDE"},
                text=latest.sort_values("overall_score")["overall_score"]
                    .apply(lambda x: f"{x*100:.1f}%"),
            )
            fig.add_vline(x=0.75, line_dash="dash", line_color="orange",
                          annotation_text="75% threshold")
            fig.update_layout(height=350, coloraxis_showscale=False)
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("Rules Passed vs Failed")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name="Passed", x=latest["cde"],
                y=latest["rules_passed"], marker_color="#2ca02c"
            ))
            fig2.add_trace(go.Bar(
                name="Failed", x=latest["cde"],
                y=latest["rules_failed"], marker_color="#d62728"
            ))
            fig2.update_layout(barmode="stack", height=350,
                               xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Exception heatmap by country ─────────────────────────────────
        st.subheader("Completeness Heatmap — Refined Layer")
        if not refined_df.empty:
            pivot = refined_df.pivot_table(
                index="country_code",
                columns="indicator",
                values="value_refined",
                aggfunc=lambda x: x.notna().mean() * 100,
            ).round(1)
            fig3 = px.imshow(
                pivot,
                color_continuous_scale="RdYlGn",
                range_color=[0, 100],
                labels={"color": "Completeness %"},
                aspect="auto",
                text_auto=".0f",
            )
            fig3.update_layout(height=500)
            st.plotly_chart(fig3, use_container_width=True)

        # ── Quality exceptions table ───────────────────────────────────
        st.subheader("Quality Exceptions Detail")
        if not quality_df.empty:
            cde_filter = st.selectbox(
                "Filter by CDE",
                ["All"] + sorted(quality_df["cde"].unique().tolist()),
            )
            dim_filter = st.multiselect(
                "Filter by dimension",
                options=sorted(quality_df["dimension"].unique().tolist()),
                default=[],
            )
            show_failures = st.checkbox("Show failures only", value=True)

            filtered = quality_df.copy()
            if cde_filter != "All":
                filtered = filtered[filtered["cde"] == cde_filter]
            if dim_filter:
                filtered = filtered[filtered["dimension"].isin(dim_filter)]
            if show_failures:
                filtered = filtered[filtered["passed"] == 0]

            display_cols = ["cde", "dimension", "rule_name", "country_code",
                            "score", "threshold", "exceptions", "severity", "detail"]
            filtered = filtered[[c for c in display_cols if c in filtered.columns]]
            st.dataframe(
                filtered.sort_values(["severity", "score"]).head(200),
                use_container_width=True, hide_index=True,
            )

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — ECONOMIC ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Economic Analysis — G20 Nations")
    st.caption("Business-ready layer · Economic Health Scores 2005–2023")

    if scores_df.empty:
        st.warning("No business-ready data. Run the full pipeline first.")
    else:
        scores_df["year"] = scores_df["year"].astype(int)

        # ── Controls ──────────────────────────────────────────────────────
        col1, col2 = st.columns([3, 1])
        with col2:
            year_range = st.slider(
                "Year range",
                min_value=int(scores_df["year"].min()),
                max_value=int(scores_df["year"].max()),
                value=(2010, int(scores_df["year"].max())),
            )
            selected_countries = st.multiselect(
                "Countries",
                options=sorted(scores_df["country_name"].unique().tolist()),
                default=["United States", "China", "Germany",
                         "India", "Japan", "Brazil"],
            )

        filtered = scores_df[
            (scores_df["year"].between(*year_range)) &
            (scores_df["country_name"].isin(selected_countries if selected_countries
                                             else scores_df["country_name"].unique()))
        ]

        with col1:
            st.subheader("Economic Health Score Over Time")
            fig = px.line(
                filtered.dropna(subset=["health_score"]),
                x="year", y="health_score",
                color="country_name",
                labels={"health_score": "Health Score (0–100)", "year": "Year",
                        "country_name": "Country"},
                hover_data=["health_tier", "indicators_available"],
            )
            fig.update_layout(height=380, hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ── Latest year snapshot ──────────────────────────────────────────
        latest_year = int(scores_df["year"].max())
        latest_snap = scores_df[scores_df["year"] == latest_year].copy()

        st.subheader(f"Snapshot: {latest_year}")
        c1, c2 = st.columns(2)

        with c1:
            fig2 = px.bar(
                latest_snap.sort_values("health_score", ascending=True)
                           .dropna(subset=["health_score"]),
                x="health_score", y="country_name",
                orientation="h",
                color="health_tier",
                color_discrete_map={
                    "Strong": "#2ca02c", "Moderate": "#ff7f0e",
                    "Weak": "#d62728", "Fragile": "#7f0000"
                },
                labels={"health_score": "Health Score", "country_name": ""},
                text="health_score",
            )
            fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig2.update_layout(height=500, showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)

        with c2:
            indicator = st.selectbox("Indicator", [
                "gdp_per_capita", "inflation", "unemployment",
                "current_account_pct", "govt_debt_pct"
            ])
            fig3 = px.bar(
                latest_snap.sort_values(indicator, ascending=True)
                           .dropna(subset=[indicator]),
                x=indicator, y="country_name", orientation="h",
                color=indicator,
                color_continuous_scale="Blues",
                labels={indicator: indicator.replace("_", " ").title(),
                        "country_name": ""},
            )
            fig3.update_layout(height=500, coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)

        # ── Scatter: GDP vs Unemployment ──────────────────────────────────
        st.subheader("GDP Per Capita vs Unemployment Rate")
        scatter_year = st.slider("Year", int(scores_df["year"].min()),
                                 int(scores_df["year"].max()), latest_year,
                                 key="scatter_year")
        scatter_df = scores_df[scores_df["year"] == scatter_year].dropna(
            subset=["gdp_per_capita", "unemployment", "health_score"]
        )
        fig4 = px.scatter(
            scatter_df,
            x="gdp_per_capita", y="unemployment",
            size="health_score", color="health_tier",
            hover_name="country_name",
            color_discrete_map={
                "Strong": "#2ca02c", "Moderate": "#ff7f0e",
                "Weak": "#d62728", "Fragile": "#7f0000"
            },
            log_x=True,
            labels={
                "gdp_per_capita": "GDP Per Capita (USD, log scale)",
                "unemployment": "Unemployment (%)",
            },
            size_max=50,
        )
        fig4.update_layout(height=420)
        st.plotly_chart(fig4, use_container_width=True)

        # ── Raw data table ─────────────────────────────────────────────────
        with st.expander("View raw business-ready data"):
            st.dataframe(filtered.sort_values(["country_name", "year"]),
                         use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — DATA CATALOG
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("Data Catalog")
    st.caption("CDE metadata, lineage, ownership, and live quality scores")

    if catalog_df.empty:
        st.warning("Catalog not built yet. Run `python -m pipeline.run_pipeline --from catalog`")
    else:
        search = st.text_input("🔍 Search catalog (name, domain, description...)", "")

        display = catalog_df.copy()
        if search:
            mask = display.apply(
                lambda col: col.astype(str).str.contains(search, case=False, na=False)
            ).any(axis=1)
            display = display[mask]

        for _, row in display.iterrows():
            score = row.get("quality_score_pct")
            score_label = f"{score:.1f}%" if pd.notna(score) else "Not assessed"
            status = row.get("quality_status", "NOT_ASSESSED")

            with st.expander(
                f"{status_badge(status)}  **{row['business_name']}**"
                f"  |  Domain: {row['domain']}"
                f"  |  Quality: {score_label}"
            ):
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.markdown("**Identity**")
                    st.write(f"Asset ID: `{row['asset_id']}`")
                    st.write(f"Indicator code: `{row['indicator_code']}`")
                    st.write(f"Privacy: `{row['privacy_class']}`")
                    st.write(f"Critical CDE: {'✅ Yes' if row.get('critical_cde') else '❌ No'}")
                    st.markdown("**Description**")
                    st.caption(row.get("description", ""))

                with c2:
                    st.markdown("**Quality**")
                    st.metric("Overall Score", score_label)
                    rules_passed = row.get("rules_passed")
                    rules_failed = row.get("rules_failed")
                    if pd.notna(rules_passed):
                        st.write(f"Rules: {int(rules_passed)} passed / {int(rules_failed)} failed")
                        st.write(f"Exceptions: {int(row.get('total_exceptions', 0))}")
                    st.write(f"Last assessed: {str(row.get('last_assessed','–'))[:19]}")
                    st.markdown("**Thresholds**")
                    st.write(f"Completeness min: {row.get('completeness_threshold_pct')}%")
                    try:
                        vr = json.loads(row.get("value_range", "[]"))
                        if vr:
                            st.write(f"Value range: [{vr[0]}, {vr[1]}]")
                    except Exception:
                        pass

                with c3:
                    st.markdown("**Lineage**")
                    st.write(f"📥 Source: {row.get('lineage_source','–')}")
                    st.write(f"🟦 Raw: `{row.get('lineage_raw','–')}`")
                    st.write(f"🟨 Refined: `{row.get('lineage_refined','–')}`")
                    st.write(f"🟩 Business ready: `{row.get('lineage_business','–')}`")
                    st.markdown("**Freshness**")
                    st.write(f"Latest year: {row.get('latest_year','–')}")
                    total = row.get("total_rows")
                    non_null = row.get("non_null_rows")
                    if pd.notna(total) and pd.notna(non_null):
                        st.write(f"Non-null rows: {int(non_null):,} / {int(total):,}")
                    try:
                        dims = json.loads(row.get("quality_dims", "[]"))
                        if dims:
                            st.markdown("**Quality dimensions monitored**")
                            st.write(" · ".join(dims))
                    except Exception:
                        pass
