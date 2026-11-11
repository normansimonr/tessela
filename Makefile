.PHONY: help install install-dev test lint format check demo

help:
	@echo "Tessela development targets:"
	@echo "  make install       install runtime dependencies"
	@echo "  make install-dev   install runtime + lint/type/test tools"
	@echo "  make test          run the test suite"
	@echo "  make lint          run ruff and mypy"
	@echo "  make format        auto-fix and format with ruff"
	@echo "  make check         run lint and tests"
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

demo:
	python3 scripts/demo.py "DEU 32:8"
