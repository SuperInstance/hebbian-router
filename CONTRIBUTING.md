# Contributing to hebbian-router

Thank you for your interest in the Cocapn Fleet. This document covers how to set up the project, run tests, and submit changes.

## Setup

```bash
git clone https://github.com/SuperInstance/hebbian-router.git
cd hebbian-router
pip install -e ".[dev]"
```

## Running Tests

```bash
# Full suite
python -m pytest tests/ -q

# With coverage
python -m pytest tests/ --cov=hebbian_router --cov-report=term-missing

# Single file
python -m pytest tests/test_core.py -v
```

## Lint & Type Check

```bash
ruff check hebbian_router/
mypy hebbian_router/ --ignore-missing-imports
```

## Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Submitting Changes

1. **Branch**: Create a feature branch (`git checkout -b feature/name`)
2. **Tests**: All tests must pass. New features need new tests.
3. **Coverage**: Maintain or improve coverage (current threshold: 75%)
4. **Commit**: Use conventional commits (`feat:`, `fix:`, `docs:`, `test:`)
5. **PR**: Open against `main` with a clear description

## Code Style

- **Ruff** for linting and formatting
- **MyPy** for type checking (ignore missing imports for external deps)
- Docstrings for public APIs
- Type hints on function signatures

## Architecture Notes

- **Hebbian plasticity**: Routes strengthen with successful use, weaken with disuse
- **Core module**: `hebbian_router/core.py` — routing table with weight decay
- **Tests**: Mirror the source structure under `tests/`

## Security

- Never commit secrets, API keys, or private keys
- Run `bandit -r .` before submitting
- The CI runs `trufflehog` to catch leaked credentials

## Questions?

Open an issue or reach out in `#cocapn-build` on Matrix.
