.PHONY: help install install-dev test lint format check data data-samaritan data-dss data-septuagint examples demo

help:
	@echo "Tessela development targets:"
	@echo "  make install       install runtime dependencies"
	@echo "  make install-dev   install runtime + lint/type/test tools"
	@echo "  make test          run the test suite"
	@echo "  make lint          run ruff and mypy"
	@echo "  make format        auto-fix and format with ruff"
	@echo "  make check         run lint and tests"
	@echo "  make data          fetch all non-commercial datasets into data/derived/"
	@echo "  make data-samaritan  fetch the Samaritan Hebrew text"
	@echo "  make data-dss        fetch the Dead Sea Scrolls readings (~2.5 GB clone)"
	@echo "  make data-septuagint rebuild the Tov corpus from local .par files"
	@echo "  make examples      render example dossiers into data/derived/examples/"
	@echo "  make demo          print the MT / SP / DSS comparison for DEU 32:8"

install:
	python3 -m pip install -r requirements.txt

install-dev:
	python3 -m pip install -r requirements-dev.txt

test:
	python3 -m pytest

lint:
	ruff check .
	mypy src

format:
	ruff check --fix .
	ruff format .

check: lint test

data:
	python3 scripts/fetch_data.py all

data-samaritan:
	python3 scripts/fetch_data.py samaritan

data-dss:
	python3 scripts/fetch_data.py dss

data-septuagint:
	python3 scripts/fetch_data.py septuagint

examples:
	mkdir -p data/derived/examples
	./scripts/tessela dossier "DEU 32:8" --out data/derived/examples/DEU-32-8.md
	./scripts/tessela dossier "GEN 2:2" --out data/derived/examples/GEN-2-2.md
	./scripts/tessela dossier "DEU 27:4" --out data/derived/examples/DEU-27-4.md

demo:
	python3 scripts/demo.py "DEU 32:8"
