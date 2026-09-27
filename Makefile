NAME = fly-in

PYTHON = python3
PIP = $(PYTHON) -m pip
MYPY = mypy
FLAKE8 = flake8

.PHONY: all install run debug clean fclean re lint lint-strict

all: run

install:
	$(PIP) install pygame mypy flake8

run:
	$(PYTHON) -m src.main $(MAP)

debug:
	$(PYTHON) -m pdb -m src.main $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

fclean: clean

re: fclean all

lint:
	$(FLAKE8) .
	$(MYPY) . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(FLAKE8) .
	$(MYPY) . --strict