<p align="center">
    <img alt="kitconcept GmbH" width="200px" src="https://kitconcept.com/logo.svg">
</p>

<h1 align="center">kitconcept.solr</h1>
<h3 align="center">An opinionated Solr integration for Plone</h3>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/kitconcept.solr)](https://pypi.org/project/kitconcept.solr/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kitconcept.solr)](https://pypi.org/project/kitconcept.solr/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/kitconcept.solr)](https://pypi.org/project/kitconcept.solr/)
[![PyPI - License](https://img.shields.io/pypi/l/kitconcept.solr)](https://pypi.org/project/kitconcept.solr/)
[![PyPI - Status](https://img.shields.io/pypi/status/kitconcept.solr)](https://pypi.org/project/kitconcept.solr/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/kitconcept.solr)](https://pypi.org/project/kitconcept.solr/)

[![Meta](https://github.com/kitconcept/kitconcept.solr/actions/workflows/meta.yml/badge.svg)](https://github.com/kitconcept/kitconcept.solr/actions/workflows/meta.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/kitconcept/kitconcept.solr)](https://github.com/kitconcept/kitconcept.solr)
[![GitHub Repo stars](https://img.shields.io/github/stars/kitconcept/kitconcept.solr?style=social)](https://github.com/kitconcept/kitconcept.solr)

</div>

## Features

`kitconcept.solr` is an opinionated Solr integration package for Plone sites. It leverages (and depends on) [`collective.solr`](https://github.com/collective/collective.solr), by adding a new endpoint `@solr` that supports search requests with facetted results.

### Endpoints

| name | context |
| -- | -- |
| `@solr` | Plone site or Folderish content |

## Documentation

### Installation

Add `kitconcept.solr` as a dependency on your package's `setup.py`

```python
    install_requires = [
        "kitconcept.solr",
        "Plone",
        "plone.restapi",
        "setuptools",
    ],
```

Also, add `kitconcept.solr` to your package's `configure.zcml` (or `dependencies.zcml`):

```xml
<include package="kitconcept.solr" />
```

### Generic Setup

To automatically enable this package when your add-on is installed, add the following line inside the package's `profiles/default/metadata.xml` `dependencies` element:

```xml
    <dependency>profile-kitconcept.solr:default</dependency>
```

## Source Code and Contributions

We welcome contributions to `kitconcept.solr`.

You can create an issue in the issue tracker, or contact a maintainer.

- [Issue Tracker](https://github.com/kitconcept/kitconcept.solr/issues)
- [Source Code](https://github.com/kitconcept/kitconcept.solr/)

### Development requirements

* Python 3.8 or later
* Docker

### Setup

Install all development dependencies -- including Plone -- and create a new instance using:

```bash
make install
```

By default, we use the latest Plone version in the 6.x series.

### Configurations

Most of the development configuration is managed with [`plone.meta`](https://github.com/plone/plone.meta), so avoid manually editing the following files:

* `.editorconfig`
* `.flake8`
* `.gitignore`
* `.pre-commit-config.yaml`
* `news/.changelog_template.jinja`
* `pyproject.toml`
* `tox.ini`

### Update translations

```bash
make i18n
```
### Format codebase

```bash
make format
```
### Run tests

Testing of this package is done with [`pytest`](https://docs.pytest.org/) and [`tox`](https://tox.wiki/).

Run all tests with:

```bash
make test
```

Run all tests but stop on the first error and open a `pdb` session:

```bash
./bin/tox -e test -- -x --pdb
```

Run only tests that match `TestEndpointEncoding`:

```bash
./bin/tox -e test -- -k TestEndpointEncoding
```

Run only tests that match `TestEndpointEncoding`, but stop on the first error and open a `pdb` session:

```bash
./bin/tox -e test -- -k TestEndpointEncoding -x --pdb
```


## License

The project is licensed under GPLv2.
