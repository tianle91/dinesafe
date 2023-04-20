.DEFAULT_GOAL := .git/hooks/pre-commit

.PHONY: clean
clean:
	rm -rf .tox .cache .venv .git/hooks/pre-commit

.venv:
	poetry config virtualenvs.in-project true
	poetry install

.git/hooks/pre-commit: .venv
	.venv/bin/python -m pre_commit install
