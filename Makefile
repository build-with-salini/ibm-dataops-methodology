.PHONY: install run run-from test lint clean dashboard help

help:
	@echo ""
	@echo "DataOps Economics Pipeline"
	@echo "──────────────────────────"
	@echo "  make install       Install Python dependencies"
	@echo "  make run           Run full pipeline (ingest → assess → remediate → transform → catalog)"
	@echo "  make run-from s=X  Resume pipeline from stage X (e.g. make run-from s=assess)"
	@echo "  make dashboard     Launch Streamlit dashboard"
	@echo "  make test          Run unit tests"
	@echo "  make lint          Run ruff linter"
	@echo "  make clean         Remove generated data and logs"
	@echo ""

install:
	pip install -r requirements.txt

run:
	python -m pipeline.run_pipeline

run-from:
	python -m pipeline.run_pipeline --from $(s)

dashboard:
	streamlit run dashboard/app.py

test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ pipeline/ dashboard/

clean:
	rm -f data/economics.db
	rm -f data/economics.db-journal
	rm -f pipeline/pipeline.log
	rm -f catalog/data_catalog.yml
	rm -f reports/quality_report.html
	rm -rf .pytest_cache
	rm -rf src/__pycache__ config/__pycache__ pipeline/__pycache__ tests/__pycache__
	rm -f .DS_Store tests/.DS_Store
	@echo "Cleaned generated files."
