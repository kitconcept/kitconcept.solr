### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

BACKEND_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
GIT_FOLDER=$(BACKEND_FOLDER)/.git

COMPOSE_PROJECT_NAME=kitconcept_solr
SOLR_DATA_FOLDER?=${BACKEND_FOLDER}/data
SOLR_ONLY_COMPOSE?=${BACKEND_FOLDER}/docker-compose.yml

# Python checks
PYTHON?=python3

# installed?
ifeq (, $(shell which $(PYTHON) ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif

# version ok?
PYTHON_VERSION_MIN=3.8
PYTHON_VERSION_OK=$(shell $(PYTHON) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_VERSION_MIN)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
  $(error "Need python $(PYTHON_VERSION) >= $(PYTHON_VERSION_MIN)")
endif

all: install

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: clean-build clean-pyc clean-test clean-venv clean-instance ## remove all build, test, coverage and Python artifacts

.PHONY: clean-instance
clean-instance: ## remove existing instance
	rm -fr instance etc inituser var

.PHONY: clean-venv
clean-venv: ## remove virtual environment
	rm -fr bin include lib lib64 env pyvenv.cfg .tox .pytest_cache requirements-mxdev.txt
	cp constraints-6.1.txt constraints.txt
	cp requirements-6.1.txt requirements.txt

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/

bin/pip bin/tox bin/mxdev:
	@echo "$(GREEN)==> Setup Virtual Env$(RESET)"
	$(PYTHON) -m venv .
	bin/pip install -U "pip" "wheel" "cookiecutter" "mxdev" "tox" "pre-commit"
	if [ -d $(GIT_FOLDER) ]; then bin/pre-commit install; else echo "$(RED) Not installing pre-commit$(RESET)";fi

constraints-mxdev.txt:  bin/tox
	bin/tox -e init

.PHONY: config
config: bin/pip  ## Create instance configuration
	@echo "$(GREEN)==> Create instance configuration$(RESET)"
	bin/cookiecutter -f --no-input -c 2.1.1 --config-file instance.yaml gh:plone/cookiecutter-zope-instance

.PHONY: install-plone-6.1
install-plone-6.1: bin/mxdev config ## pip install Plone packages
	@echo "$(GREEN)==> Setup Build$(RESET)"
	cp constraints-6.1.txt constraints.txt
	cp requirements-6.1.txt requirements.txt
	bin/tox -e init
	bin/mxdev -c mx.ini
	bin/pip install -r requirements-mxdev.txt

.PHONY: install-plone-5.2
install-plone-5.2: bin/mxdev config ## pip install Plone packages
	@echo "$(GREEN)==> Setup Build$(RESET)"
	cp constraints-5.2.txt constraints.txt
	cp requirements-5.2.txt requirements.txt
	bin/tox -e init
	bin/mxdev -c mx.ini
	bin/pip install -r requirements-mxdev.txt

.PHONY: install
install: install-plone-6.1  ## Install Plone 6.1

.PHONY: start
start: ## Start a Plone instance on localhost:8080
	PYTHONWARNINGS=ignore ./bin/runwsgi instance/etc/zope.ini

.PHONY: format
format: bin/tox ## Format the codebase according to our standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	bin/tox -e format

.PHONY: lint
lint: bin/tox ## check code style
	bin/tox -e lint

# i18n
bin/i18ndude bin/pocompile: bin/pip
	@echo "$(GREEN)==> Install translation tools$(RESET)"
	bin/pip install i18ndude zest.pocompile

.PHONY: i18n
i18n: bin/i18ndude ## Update locales
	@echo "$(GREEN)==> Updating locales$(RESET)"
	bin/update_locale
	bin/pocompile src/

# Tests
.PHONY: test
test: bin/tox constraints-mxdev.txt ## run tests
	bin/tox -e test

.PHONY: coverage
coverage: bin/tox constraints-mxdev.txt ## run coverage
	bin/tox -e coverage

## Solr docker utils
test-compose-project-name:
	# The COMPOSE_PROJECT_NAME env variable must exist and discriminate between your projects,
	# and the purpose of the container (_DEV, _STACK, _TEST)
	test -n "$(COMPOSE_PROJECT_NAME)"

.PHONY: solr-start
solr-start: test-compose-project-name ## Start solr
	@echo "Start solr"
	@COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker compose -f ${SOLR_ONLY_COMPOSE} up -d

.PHONY: solr-start-fg
solr-start-fg: test-compose-project-name ## Start solr in foreground
	@echo "Start solr in foreground"
	@COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker compose -f ${SOLR_ONLY_COMPOSE} up

.PHONY: solr-stop
solr-stop: test-compose-project-name ## Stop solr
	@echo "Stop solr"
	@COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker compose -f ${SOLR_ONLY_COMPOSE} down

.PHONY: solr-logs
solr-logs: test-compose-project-name ## Show solr logs
	@echo "Show solr logs"
	@COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker compose -f ${SOLR_ONLY_COMPOSE} logs -f

.PHONY: release
release: ## make a new release
	bin/fullrelease
