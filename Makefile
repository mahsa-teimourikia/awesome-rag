# Convenience targets for the credential-free RAG course environment.
# Override VENV or PYTHON when needed, for example: make VENV=.venv setup

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
PIP = $(PYTHON) -m pip

.PHONY: help setup install test notebooks notebook-check links pages external-links clean

help:
	@echo "make setup          Create the virtual environment and install developer tools"
	@echo "make test           Run the deterministic Python test suite"
	@echo "make notebooks      Start Jupyter Lab for the course notebooks"
	@echo "make notebook-check Execute all credential-free notebooks in Jupyter kernels"
	@echo "make links          Validate Learning Hub resource paths"
	@echo "make pages          Build and smoke-test the GitHub Pages Hub and quiz"
	@echo "make external-links Check curated external links (network required)"

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[dev]'

install: setup

test:
	PYTHONPATH=. $(PYTHON) -m pytest -q

notebooks:
	PYTHONPATH=. $(PYTHON) -m jupyterlab notebooks

notebook-check:
	PYTHONPATH=. $(PYTHON) scripts/execute-notebooks.py --timeout 90

links:
	node scripts/validate-learning-links.mjs

pages:
	npm ci
	npm run test:pages

external-links:
	node scripts/check-external-links.mjs

clean:
	@echo "Generated Python and Pages artifacts are intentionally not removed automatically."
