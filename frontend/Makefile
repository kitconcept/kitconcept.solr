# Yeoman Volto App development

### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Recipe snippets for reuse

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

PLONE_VERSION=6
VOLTO_VERSION=17.0.0-alpha.24

ADDON_NAME='@kitconcept/volto-solr'
ADDON_PATH='volto-solr'
DEV_COMPOSE=dockerfiles/docker-compose.yml
ACCEPTANCE_COMPOSE=acceptance/docker-compose.yml
SOLR_CONTEXT_FOLDER=${CURRENT_DIR}/acceptance/solr
CMD=CURRENT_DIR=${CURRENT_DIR} ADDON_NAME=${ADDON_NAME} ADDON_PATH=${ADDON_PATH} VOLTO_VERSION=${VOLTO_VERSION} PLONE_VERSION=${PLONE_VERSION} SOLR_CONTEXT_FOLDER=${SOLR_CONTEXT_FOLDER} docker compose
# CMD=CURRENT_DIR=${CURRENT_DIR} ADDON_NAME=${ADDON_NAME} ADDON_PATH=${ADDON_PATH} VOLTO_VERSION=${VOLTO_VERSION} PLONE_VERSION=${PLONE_VERSION} docker compose
DOCKER_COMPOSE=${CMD} -p ${ADDON_PATH} -f ${DEV_COMPOSE}
ACCEPTANCE=${CMD} -p ${ADDON_PATH}-acceptance -f ${ACCEPTANCE_COMPOSE}

# Dev Helpers
.PHONY: i18n
i18n: ## Sync i18n
	${DOCKER_COMPOSE} run addon-dev i18n

.PHONY: format
format: ## Format codebase
	${DOCKER_COMPOSE} run addon-dev lint:fix
	${DOCKER_COMPOSE} run addon-dev prettier:fix
	${DOCKER_COMPOSE} run addon-dev stylelint:fix

.PHONY: lint
lint: ## Lint Codebase
	${DOCKER_COMPOSE} run addon-dev lint
	${DOCKER_COMPOSE} run addon-dev prettier
	${DOCKER_COMPOSE} run addon-dev stylelint

.PHONY: test
test: ## Run unit tests
	${DOCKER_COMPOSE} run addon-dev test --watchAll

.PHONY: test-ci
test-ci: ## Run unit tests in CI
	${DOCKER_COMPOSE} run -e CI=1 addon-dev test

## Acceptance
.PHONY: install-acceptance
install-acceptance: ## Install Cypress, build containers
	(cd acceptance && yarn)
	${ACCEPTANCE} --profile dev --profile prod build

.PHONY: start-test-acceptance-server
start-test-acceptance-server: ## Start acceptance server
	${ACCEPTANCE} --profile dev up -d

.PHONY: start-test-acceptance-server-prod
start-test-acceptance-server-prod: ## Start acceptance server
	${ACCEPTANCE} --profile prod up -d

.PHONY: test-acceptance
test-acceptance: ## Start Cypress
	(cd acceptance && ./node_modules/.bin/cypress open)

.PHONY: test-acceptance-headless
test-acceptance-headless: ## Run cypress tests in CI
	(cd acceptance && ./node_modules/.bin/cypress run)

.PHONY: stop-test-acceptance-server
stop-test-acceptance-server: ## Stop acceptance server
	${ACCEPTANCE} down

.PHONY: status-test-acceptance-server
status-test-acceptance-server: ## Status of Acceptance Server
	${ACCEPTANCE} ps
