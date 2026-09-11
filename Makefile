NAME = fly-in

PYTHON = python3
MYPY = mypy
FLAKE8 = flake8

.PHONY: all check clean fclean re

all:
	$(PYTHON) -m src.main $(MAP)

check:
	$(MYPY) src
	$(FLAKE8) src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean

re: fclean all