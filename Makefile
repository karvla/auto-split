SRC_DIR := .

format:
	isort $(SRC_DIR)
	black $(SRC_DIR)

lint:
	flake8 $(SRC_DIR)

pre-commit: format lint

all: format lint
