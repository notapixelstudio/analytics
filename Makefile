# This target is executed whenever we just type `make`
.DEFAULT_GOAL = help
FILE=VERSION
VERSION=`cat $(FILE)`
COMMIT_MSG_HOOK = '\#!/bin/bash\nMSG_FILE=$$1\ncz check --allow-abort --commit-msg-file $$MSG_FILE'

install-pip-tools:
	pip install -U pip
	pip install --upgrade pip-tools

requirements-dev.txt: requirements-dev.in install-pip-tools
	pip-compile --upgrade --resolver backtracking --output-file=$@ requirements-dev.in

requirements.txt: requirements.in install-pip-tools
	pip-compile --upgrade --resolver backtracking --output-file=$@ requirements.in

install-dev: requirements-dev.txt
	pip install  -r requirements-dev.txt

install: requirements.txt
	pip install  -r requirements.txt

setup-dev-env: install-dev
	pre-commit install
	echo $(COMMIT_MSG_HOOK) > .git/hooks/commit-msg
	chmod +x .git/hooks/commit-msg

setup-dev-env-autoupdate: setup-dev-env
	pre-commit autoupdate

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} \;
	find . -type d -name .hypothesis -prune -exec rm -rf {} \;
	find . -type d -name .ipynb_checkpoints -prune -exec rm -rf {} \;
	find . -type d -name .pytest_cache -prune -exec rm -rf {} \;
	find . -type d -name .mypy_cache -prune -exec rm -rf {} \;

ndef = $(if $(value $(1)),,$(error $(1) not set, provide $(1), e.g. make $(1)=<value> <target>))

echo-version:
	$(call ndef,VERSION)
	@echo $(VERSION)

fetch-tags:
	git fetch --tags

changelog: setup-dev-env
	cz changelog --unreleased-version $(VERSION)

# this will update the version, changelog, tag and commit
bump: fetch-tags setup-dev-env
	cz bump

bump-minor: fetch-tags setup-dev-env
	cz bump --increment MINOR

bump-major: fetch-tags setup-dev-env
	cz bump --increment MAJOR

bump-patch: fetch-tags setup-dev-env
	cz bump --increment PATCH
