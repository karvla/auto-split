SRC_DIR := .

install:
	pip install poetry
	poetry install

run:
	poetry run python3 car_pool/main.py

format:
	isort $(SRC_DIR)
	black $(SRC_DIR)

lint:
	flake8 $(SRC_DIR)

test:
	pytest $(SRC_DIR)

pre-commit: format lint test

all: format lint test
