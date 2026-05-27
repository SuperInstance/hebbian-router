.PHONY: test lint type-check coverage security install clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -q --tb=short

test-verbose:
	python -m pytest tests/ -v --tb=short

coverage:
	python -m pytest tests/ --cov=hebbian_router --cov-report=term-missing --cov-fail-under=75

lint:
	ruff check hebbian_router/

format:
	ruff format hebbian_router/

type-check:
	mypy hebbian_router/ --ignore-missing-imports

security:
	bandit -r hebbian_router/
	pip-audit --desc .

dev: install lint type-check test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/
