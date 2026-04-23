SHELL := /bin/bash
PYTHON := python
PIP    := pip

.DEFAULT_GOAL := help

# ─────────────────────────────────────────────────────────────
# HELP
# ─────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  SQL → MongoDB Transpiler — available targets"
	@echo "  ─────────────────────────────────────────────"
	@echo "  make setup          Run setup.sh + install Python dependencies"
	@echo "  make install        (Re)install Python dependencies"
	@echo "  make run            Run the CLI transpiler  (main.py)"
	@echo "  make verify         Run the Flask web app   (app.py)"
	@echo "  make webapp         Run the FastAPI web app (webapp/main.py)"
	@echo "  make test           Run the full pytest suite"
	@echo "  make clean          Remove __pycache__ and generated artefacts"
	@echo ""

# ─────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────

.PHONY: setup
setup:
	@echo ">>> Running setup.sh (system deps + PostgreSQL + MongoDB) ..."
	bash setup.sh
	@echo ">>> Setup complete. Run 'make help' to see what you can do next."

.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# ─────────────────────────────────────────────────────────────
# RUN TARGETS
# ─────────────────────────────────────────────────────────────

# CLI transpiler — override defaults with: make run SQL=query2.sql SCHEMA=schema2.json
SQL    ?= query.sql
SCHEMA ?= schema.json

.PHONY: run
run:
	@echo ">>> Running CLI transpiler (main.py) with $(SQL) ..."
	$(PYTHON) main.py $(SQL) $(SCHEMA)

# Flask web app (development server)
.PHONY: verify
verify:
	@echo ">>> Checking if port 5000 is in use ..."
	@fuser -k 5000/tcp 2>/dev/null && echo ">>> Killed process on port 5000." || echo ">>> Port 5000 is free."
	@echo ">>> Starting Flask app on http://127.0.0.1:5000 ..."
	FLASK_APP=app.py FLASK_ENV=development $(PYTHON) -m flask run --host=0.0.0.0 --port=5000

# FastAPI web app (webapp/main.py) via Uvicorn
.PHONY: webapp
webapp:
	@echo ">>> Checking if port 8000 is in use ..."
	@fuser -k 8000/tcp 2>/dev/null && echo ">>> Killed process on port 8000." || echo ">>> Port 8000 is free."
	@echo ">>> Starting FastAPI webapp — open http://127.0.0.1:8000 in your browser ..."
	python -m uvicorn webapp.main:app --host 0.0.0.0 --port 8000 --reload

# ─────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────

.PHONY: test
test:
	@echo ">>> Running pytest ..."
	$(PYTHON) -m pytest tests/test_transpiler_full.py -v

# ─────────────────────────────────────────────────────────────
# CLEAN
# ─────────────────────────────────────────────────────────────

.PHONY: clean
clean:
	@echo ">>> Cleaning up ..."
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "parser.out" -delete 2>/dev/null || true
	find . -name "parsetab.py" -delete 2>/dev/null || true
	@echo ">>> Clean done."
