.DEFAULT_GOAL := venv

.PHONY: clean
clean:
	rm -rf .tox .cache venv

venv:
	poetry config virtualenvs.path venv
	poetry install
