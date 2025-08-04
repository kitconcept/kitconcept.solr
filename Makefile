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
GIT_FOLDER=$(CURRENT_DIR)/.git

PROJECT_NAME=kitconcept.solr
STACK_NAME=kitconcept-solr
STACK_FILE=docker-compose.yml
STACK_FILE_DEV=docker-compose-dev.yml
STACK_FILE_CI=docker-compose-ci.yml
STACK_HOSTNAME=kitconcept-solr.localhost

VOLTO_VERSION=$(shell cat frontend/mrs.developer.json | python -c "import sys, json; print(json.load(sys.stdin)['core']['tag'])")
PLONE_VERSION=$(shell cat backend/version.txt)

# Environment variables to be exported
export VOLTO_VERSION := $(VOLTO_VERSION)
export PLONE_VERSION := $(PLONE_VERSION)
export DOCKER_BUILDKIT := 1
export COMPOSE_BAKE := 1
export STACK_HOSTNAME := $(STACK_HOSTNAME)

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

.PHONY: all
all: install

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

###########################################
# Frontend
###########################################
.PHONY: frontend-install
frontend-install:  ## Install React Frontend
	$(MAKE) -C "./frontend/" install

.PHONY: frontend-build
frontend-build:  ## Build React Frontend
	$(MAKE) -C "./frontend/" build

.PHONY: frontend-start
frontend-start:  ## Start React Frontend
	$(MAKE) -C "./frontend/" start

.PHONY: frontend-test
frontend-test:  ## Test frontend codebase
	@echo "Test frontend"
	$(MAKE) -C "./frontend/" test

###########################################
# Backend
###########################################
.PHONY: backend-install
backend-install:  ## Create virtualenv and install Plone
	$(MAKE) -C "./backend/" install
	$(MAKE) backend-create-site

.PHONY: backend-build
backend-build:  ## Build Backend
	$(MAKE) -C "./backend/" install

.PHONY: backend-create-site
backend-create-site: ## Create a Plone site with default content
	$(MAKE) -C "./backend/" create-site

.PHONY: backend-update-example-content
backend-update-example-content: ## Export example content inside package
	$(MAKE) -C "./backend/" update-example-content

.PHONY: backend-start
backend-start: ## Start Plone Backend
	$(MAKE) -C "./backend/" start

.PHONY: backend-test
backend-test:  ## Test backend codebase
	@echo "Test backend"
	$(MAKE) -C "./backend/" test

###########################################
# Environment
###########################################
.PHONY: install
install:  ## Install
	@echo "Install Backend & Frontend"
	$(MAKE) backend-install
	$(MAKE) frontend-install

.PHONY: clean
clean:  ## Clean installation
	@echo "Clean installation"
	$(MAKE) -C "./backend/" clean
	$(MAKE) -C "./frontend/" clean

###########################################
# QA
###########################################
.PHONY: format
format:  ## Format codebase
	@echo "Format the codebase"
	$(MAKE) -C "./backend/" format
	$(MAKE) -C "./frontend/" format

.PHONY: lint
lint:  ## Format codebase
	@echo "Lint the codebase"
	$(MAKE) -C "./backend/" lint
	$(MAKE) -C "./frontend/" lint

.PHONY: check
check:  format lint ## Lint and Format codebase

###########################################
# i18n
###########################################
.PHONY: i18n
i18n:  ## Update locales
	@echo "Update locales"
	$(MAKE) -C "./backend/" i18n
	$(MAKE) -C "./frontend/" i18n

###########################################
# Testing
###########################################
.PHONY: test
test:  backend-test frontend-test ## Test codebase

###########################################
# Container images
###########################################
.PHONY: build-images
build-images:  ## Build container images
	@echo "Build"
	$(MAKE) -C "./backend/" build-image
	$(MAKE) -C "./frontend/" build-image

###########################################
# Local Stack
###########################################
.PHONY: stack-create-site
stack-create-site:  ## Local Stack: Create a new site
	@echo "Create a new site in the local Docker stack"
	@echo "(Stack must not be running already.)"
	@docker compose -f $(STACK_FILE) run --build backend ./docker-entrypoint.sh create-site

.PHONY: stack-start
stack-start:  ## Local Stack: Start Services
	@echo "Start local Docker stack"
	@docker compose -f $(STACK_FILE) up -d --build
	@echo "Now visit: http://kitconcept.solr.localhost"

.PHONY: stack-status
stack-status:  ## Local Stack: Check Status
	@echo "Check the status of the local Docker stack"
	@docker compose -f $(STACK_FILE) ps

.PHONY: stack-stop
stack-stop:  ##  Local Stack: Stop Services
	@echo "Stop local Docker stack"
	@docker compose -f $(STACK_FILE) stop

.PHONY: stack-rm
stack-rm:  ## Local Stack: Remove Services and Volumes
	@echo "Remove local Docker stack"
	@docker compose -f $(STACK_FILE) down
	@echo "Remove local volume data"
	@docker volume rm $(PROJECT_NAME)_vol-site-data

###########################################
# Acceptance
###########################################
.PHONY: acceptance-backend-dev-start
acceptance-backend-dev-start:
	@echo "Start acceptance backend and solr"
	@docker compose -f $(STACK_FILE_DEV) up backend-acceptance solr-acceptance --build

.PHONY: acceptance-frontend-dev-start
acceptance-frontend-dev-start:
	@echo "Start acceptance frontend"
	$(MAKE) -C "./frontend/" acceptance-frontend-dev-start

.PHONY: acceptance-test
acceptance-test:
	@echo "Start acceptance tests in interactive mode"
	$(MAKE) -C "./frontend/" acceptance-test

## Acceptance tests with Container
.PHONY: acceptance-images-build
acceptance-images-build: ## Build Acceptance frontend/backend images
	@echo "Build acceptance images build"
	@docker compose -f $(STACK_FILE_DEV) --profile acceptance build

.PHONY: acceptance-containers-start
acceptance-containers-start: ## Start Acceptance containers
	@echo "Start acceptance containers"
	@docker compose -f $(STACK_FILE_DEV) --profile acceptance up -d

.PHONY: acceptance-containers-stop
acceptance-containers-stop: ## Stop Acceptance containers
	@echo "Stop acceptance containers"
	@docker compose -f $(STACK_FILE_DEV) --profile acceptance down

## Acceptance tests in CI
.PHONY: ci-acceptance-images-load
ci-acceptance-images-load: ## Load Acceptance images in CI
	@echo "Load acceptance images"
	@docker compose -f $(STACK_FILE_DEV) -f $(STACK_FILE_CI) --profile ci pull

.PHONY: ci-acceptance-containers-start
ci-acceptance-containers-start: ## Start Acceptance containers
	@echo "Start acceptance containers"
	@docker compose -f $(STACK_FILE_DEV) -f $(STACK_FILE_CI) --profile ci up

.PHONY: ci-acceptance-test
ci-acceptance-test: ## Run Acceptance tests in ci mode
	@echo "Run acceptance tests"
	$(MAKE) -C "./frontend/" ci-acceptance-test

.PHONY: ci-acceptance-test-complete
ci-acceptance-test-complete: ## Simulate CI acceptance test run
	@echo "Simulate CI acceptance test run"
	$(MAKE) acceptance-containers-start
	pnpx wait-on --httpTimeout 20000 http-get://localhost:55001/plone http://localhost:3000
	$(MAKE) ci-acceptance-test
	$(MAKE) acceptance-containers-stop
