test:
	uv run coverage run -m pytest tests/ -vv
	coverage report

mypy:
	uv run mypy .

lint:
	uv run ruff check