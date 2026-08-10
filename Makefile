.PHONY: test lint format-check type check

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

lint:
	python3 -m ruff check .

format-check:
	python3 -m ruff format --check .

type:
	python3 -m mypy src/uwatt

check: format-check lint type test
