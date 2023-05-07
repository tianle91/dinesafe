.DEFAULT_GOAL := test

.PHONY: clean
clean:
	rm -rf .tox .cache .venv requirements.txt .git/hooks/pre-commit

.venv:
	poetry config virtualenvs.in-project true
	poetry install

.git/hooks/pre-commit: .venv
	.venv/bin/python -m pre_commit install

.PHONY: test
test: .git/hooks/pre-commit
	tox run
