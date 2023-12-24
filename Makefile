.DEFAULT_GOAL := test

.PHONY: clean
clean:
	rm -rf .tox .cache .venv requirements.txt .git/hooks/pre-commit **/__pycache__
	rm -rf LAST_REFRESHED_TS data/dinesafe/*.xml *.sqlite

.venv:
	poetry config virtualenvs.in-project true
	poetry install

.PHONY: pre-commit
pre-commit: .venv
	.venv/bin/python -m pre_commit install

.PHONY: test
test:
	tox run
