SRC_DIR := .

.PHONY: pre-commit test

install:
	uv sync
	uv sync --extra dev

run:
	uv run python3 auto_split/main.py

format:
	uv tool run ruff format

lint:
	uv tool run ruff check ./auto_split

test:
	uv run pytest $(SRC_DIR)

pre-commit: format lint test

all: format lint test
