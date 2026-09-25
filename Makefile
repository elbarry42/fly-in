NAME = fly-in

PYTHON = python3
MYPY = mypy
FLAKE8 = flake8

.PHONY: all install run check clean fclean re

all: run

install:
	@$(PYTHON) -c "import pygame; print('pygame: OK')"
	@$(MYPY) --version
	@$(FLAKE8) --version

run:
	$(PYTHON) -m src.main maps/easy/01_linear_path.txt

check:
	$(MYPY) src
	$(FLAKE8) src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean

re: fclean all