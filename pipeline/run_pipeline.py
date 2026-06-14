"""
run_pipeline.py  —  DataOps Orchestrator
------------------------------------------
Runs the full end-to-end pipeline in sequence:

  RAW              →  Ingest from World Bank API
  ASSESS           →  Run quality rules on raw data
  REMEDIATE        →  Cleanse and write to refined layer
  TRANSFORM        →  Build business-ready economic health scores
  CATALOG          →  Build and publish the data catalog

Each stage is logged with timing. A failed stage halts the pipeline
and logs the error — partial runs are safe (each stage is idempotent).

Usage:
    python -m pipeline.run_pipeline           # full run
    python -m pipeline.run_pipeline --from remediate  # resume from stage
"""

import sys
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

Path("pipeline").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PIPELINE] %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline/pipeline.log", mode="a"),
    ]
)
log = logging.getLogger(__name__)

STAGES = ["ingest", "assess", "remediate", "transform", "catalog"]


def run_stage(name: str) -> float:
    """Execute a named stage and return elapsed seconds."""
    t0 = time.time()
    log.info("=" * 60)
    log.info("STAGE: %s", name.upper())
    log.info("=" * 60)

    if name == "ingest":
        from src.ingest import run_ingestion
        rows = run_ingestion()
        log.info("Ingested %d rows.", rows)

    elif name == "assess":
        from src.assess import run_assessment
        summaries = run_assessment()
        for s in summaries:
            log.info("  %-28s %.1f%%  [%s]",
                     s["cde"], s["overall_score"] * 100, s["status"])

    elif name == "remediate":
        from src.remediate import run_remediation
        run_remediation()

    elif name == "transform":
        from src.transform import run_transform
        run_transform()

    elif name == "catalog":
        from src.catalog_manager import run_catalog_build
        run_catalog_build()

    elapsed = time.time() - t0
    log.info("STAGE %s completed in %.1fs", name.upper(), elapsed)
    return elapsed


def main(start_from: str = "ingest") -> None:
    started_at = datetime.now(timezone.utc).isoformat()
    log.info("Pipeline started at %s", started_at)

    start_idx = STAGES.index(start_from) if start_from in STAGES else 0
    stages_to_run = STAGES[start_idx:]

    timings = {}
    for stage in stages_to_run:
        try:
            elapsed = run_stage(stage)
            timings[stage] = elapsed
        except Exception as e:
            log.error("STAGE %s FAILED: %s", stage.upper(), e, exc_info=True)
            log.error("Pipeline halted. Fix the error and re-run with --from %s", stage)
            sys.exit(1)

    log.info("")
    log.info("Pipeline finished successfully.")
    log.info("Stage timings:")
    for stage, secs in timings.items():
        log.info("  %-12s  %.1fs", stage, secs)
    log.info("Total: %.1fs", sum(timings.values()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DataOps Economics Pipeline")
    parser.add_argument("--from", dest="start_from", default="ingest",
                        choices=STAGES, help="Resume pipeline from this stage")
    args = parser.parse_args()
    main(start_from=args.start_from)
