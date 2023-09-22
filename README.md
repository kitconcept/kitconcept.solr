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

| name    | context                         |
| ------- | ------------------------------- |
| `@solr` | Plone site or Folderish content |

#### Using the `@solr` endpoint

The `@solr` endpoint is used from the `kitconcept.volto-solr` Volto add-on package for the implementation of the site search. It can also be used for custom components. The parameters roughly follow the parameters of the normal site search service, but differ in some respects.

**TBD** _give more information about this._

For now, please refer to the source code of the `solr.py` module, in case you want to use for your own purposes.

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

#### Remark with Plone 6.0

With Plone 6.0 you must add an additional dependency `"plone.restapi>=8.40.0"`.

The package also keeps support with Plone 5.2 where `"plone.restapi>=8.21.2"` is a working version. It will not support image scales, but the package will work gracefully without displaying image previews in the search result list.

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

- Python 3.8 or later
- Docker

### Setup

Install all development dependencies -- including Plone -- and create a new instance using:

```bash
make install
```

By default, we use the latest Plone version in the 6.x series.

### Configurations

Most of the development configuration is managed with [`plone.meta`](https://github.com/plone/plone.meta), so avoid manually editing the following files:

- `.editorconfig`
- `.flake8`
- `.gitignore`
- `.pre-commit-config.yaml`
- `news/.changelog_template.jinja`
- `pyproject.toml`
- `tox.ini`

In addition there is Solr related configuration that is outlined in the following chapters.

#### Configuring Solr

Solr is configured by a default configuration that can be found in the [`/solr/etc/`](./solr/etc) folder in this repository. This contains, most notably, the `schema.xml` that defines the indexes for Solr. This package also builds docker images with the default Solr version, set up with this default configuration.

If you need to customize the Solr configuration (such as adding new indexes, etc.) then you should copy the `solr` folder into your own project, customize it as you wish, and then build your own docker images (or compile your own Solr server) based on this configuration.

A typical use case for why you would want to do this, is if you add new fields to some content types, and you want to render the values for these additional fields in the search results. In this case you want to add the additional fields as indexes to Solr. You probably would not need this, unless you change anything on the result type templates in the `kitconcept.volto-solr` front-end package.

#### Configuring the front-end and back-end packages

The package supports the usage of the `kitconcept.volto-solr` add-on, and it is designed to be used together with it.

The configuration can be specified in a customized way. Without any additional configuration, the package will use the default, which is specified in json format in the [`kitconcept.solr.interfaces.IKitconceptSolrSettings`](./src/kitconcept/solr/profiles/default/registry/kitconcept.solr.interfaces.IKitconceptSolrSettings.xml) registry.

This configuration settings affect the behavior of both the `kitconcept.solr` (this) back-end package, and the `kitconcept.volto-solr` front-end package (a Volto add-on). In addition, `kitconcept.volto-solr` has its own Volto add-on configuration which is not explained here, for these options please refer to the documentation of the add-on package.

##### Configuration options

Explanation for the configuration options:

###### `fieldList`

Contains the fields that solr should return. If the search result templates in the volto add-on are modified, and require more fields than in the default list, the fields **must explicitly be added** here.

In addition, the same fields must be present in the Solr index - if either the Solr index or the field in `fieldList` is missing, the field value will silently be not returned. No error will be shown.

Example value:

```json
[
  "UID",
  "Title",
  "Description",
  "Type",
  "effective",
  "start",
  "created",
  "end",
  "path_string",
  "mime_type",
  "phone",
  "email",
  "location",
  "image_scales",
  "image_field"
]
```

###### `searchTabs`

A list of dictionary items representing the facet tabs in the search page.

The `label` field specifies the label to be shown on the tab in English. It's the front-end package's responsibility to provide translations for this, as `kitconcept.volto-solr` does this for the defaults, which can be used as an example.

The `filter` field defines the Solr search condition to the given facet tab. This can be a content type, or in fact any condition understood by Solr, please consult the Solr documentation for more details.

Example value:

```json
[
  {
    "label": "All",
    "filter": "Type(*)"
  },
  {
    "label": "Pages",
    "filter": "Type:(Page)"
  },
  {
    "label": "Events",
    "filter": "Type:(Event)"
  },
  {
    "label": "Images",
    "filter": "Type:(Image)"
  },
  {
    "label": "Files",
    "filter": "Type:(File)"
  }
]
```

##### Overriding the configuration options

If needed, the default [`kitconcept.solr.interfaces.IKitconceptSolrSettings`](./src/kitconcept/solr/profiles/default/registry/kitconcept.solr.interfaces.IKitconceptSolrSettings.xml) can be customized in the registry via GenericSetup.

### Using reindex helpers

Helpers for activate and reindex solr are importable from the package.

Example for a reindex script that can be called from Makefile:

```py
from kitconcept.solr.reindex_helpers import activate_and_reindex
from Testing.makerequest import makerequest
from zope.site.hooks import setSite

import sys
import transaction


if __name__ == "__main__":
    app = makerequest(app)  # noQA

    # Set site to Plone
    site_id = "Plone"
    portal = app.unrestrictedTraverse(site_id)
    setSite(portal)

    activate_and_reindex(portal, clear="--clear" in sys.argv)

    transaction.commit()
    app._p_jar.sync()
```

Example for an upgrade step that adds the `kitconcept.solr` package, and one that does the solr activation for the first time:

```py
from kitconcept.solr.reindex_helpers import activate_and_reindex
from plone import api

import logging


logger = logging.getLogger("your_package_name_here")


# We suggest to add two distinct upgrade step for the package installation
# and the solr activation, in case of a failure this allows to
# identify the problem easier.


def install_kitconcept_solr(context):
    st = api.portal.get_tool("portal_setup")
    st.runAllImportStepsFromProfile("kitconcept.solr:default")
    logger.info("Installed kitconcept.solr")


def activate_and_reindex_solr(context):
    activate_and_reindex(context)
    logger.info("Activated and reindexed solr")
```

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

## Credits

The development of this add-on has been kindly sponsored by [German Aerospace Center (DLR)](https://www.dlr.de) and [Forschungszentrum Jülich](https://www.fz-juelich.de).

<img alt="German Aerospace Center (DLR)" width="200px" src="https://raw.githubusercontent.com/kitconcept/kitconcept.solr/main/docs/dlr.svg" style="background-color:white">
<img alt="Forschungszentrum Jülich" width="200px" src="https://raw.githubusercontent.com/kitconcept/kitconcept.solr/main/docs/fz-juelich.svg" style="background-color:white">

Developed by [kitconcept](https://www.kitconcept.com/)

## License

The project is licensed under GPLv2.
