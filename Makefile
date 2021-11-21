# keep in sync with: https://github.com/kitconcept/buildout/edit/master/Makefile
# update by running 'make update'
SHELL := /bin/bash
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

all: build-plone-5.2

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: Update Makefile and Buildout
update: ## Update Make and Buildout
	wget -O Makefile https://raw.githubusercontent.com/kitconcept/buildout/master/Makefile
	wget -O requirements.txt https://raw.githubusercontent.com/kitconcept/buildout/master/requirements.txt
	wget -O plone-5.2.x.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/plone-5.2.x.cfg
	wget -O versions.cfg https://raw.githubusercontent.com/kitconcept/buildout/master/versions.cfg

 ## Build Plone 5.2
.PHONY: Build Plone 5.2
build-plone-5.2:  ## Build Plone 5.2
	python3 -m venv .
	bin/pip install -r requirements.txt --upgrade
	bin/buildout -c plone-5.2.x.cfg

 ## Build Plone 6.0
 .PHONY: Build Plone 6.0
build-plone-6.0:  ## Build Plone 6.0
	python3 -m venv .
	bin/pip install -r requirements.txt --upgrade
	bin/buildout -c plone-6.0.x.cfg

 .PHONY: black
black:  ## Black
	bin/black src/ setup.py

.PHONY: flake8
flake8:  ## flake8
	bin/flake8 src/ setup.py

.PHONY: pyroma
pyroma:  ## pyroma
	bin/pyroma -n 10 -d .

.PHONY: zpretty
zpretty:  ## zpretty
	find src/ -name *.zcml | xargs zpretty -i

.PHONY: Test
test:  ## Test
	bin/test

.PHONY: Test Performance
test-performance:
	jmeter -n -t performance.jmx -l jmeter.jtl

.PHONY: Code Analysis
code-analysis:  ## Code Analysis
	bin/code-analysis

.PHONY: Test Release
test-release:  ## Run Pyroma and Check Manifest
	bin/pyroma -n 10 -d .

.PHONY: Release
release:  ## Release
	bin/fullrelease

.PHONY: Clean
clean:  ## Clean
	git clean -Xdf

.PHONY: all clean
