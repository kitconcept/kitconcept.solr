# kitconcept.solr

## Development

Requirements:

- Python 3.8

Setup:

```sh
make
```

Run Static Code Analysis:

```sh
make code-Analysis
```

Run Unit / Integration Tests:

```sh
make test
```

### Run Robot Framework based acceptance tests

Install acceptance tests:

```sh
make install-acceptance
```

Start the acceptance servers:

```sh
make start-test-acceptance-servers
```

Run the acceptance tests:

```sh
make test-acceptance
```

## Configuration

### Configuring Solr

Solr is configured by a default configuration that can be found in the [`/solr/etc/`](./solr/etc) folder in this repository. This contains, most notably, the `schema.xml` that defines the indexes for Solr. This package also builds docker images with the default Solr version, set up with this default configuration.

If you need to customize the Solr configuration (such as adding new indexes, etc.) then you should copy the `solr` folder into your own project, customize it as you wish, and then build your own docker images (or compile your own solr server) based on this configuration.

A typical use case for why you would want to do this, is if you add new fields to some content types, and you want to render the values for these additional fields in the search results. You probably would not need this, unless you change anything on the result type templates in the `volto-solr` front-end package.

### Configuring the front-end and back-end packages

The package supports the usage of the `kitconcept.volto-solr` add-on, and it is designed to be used together with it.

The configuration can be specified in a customized way. Without any additional configuration, the package will use the default which is specified in [json format](./src/kitconcept/solr/configuration/solr-config.json).

#### Configuration options

Explanation for the configuration options:

##### `fieldList`

Contains the fields that solr should return. If the search result templates in the volto add-on are modified, and requrire more fields than in the default list, the fields must explicitly be added here.

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

##### `searchTabs`

A list of dictionary items representing the facet tabs in the search page.

The `label` field specifies the label to be shown on the tab in English. It's the front-end package's responsibility to provide translations for this, as `volto-solr` does this for the defaults, which can be used as an example.

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

#### Overriding the configuration options

The configuration can be provided from a custom package by overriding the Zope utility from an `overrides.zcml` file. Example:

```xml
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">

  <utility
      provides="kitconcept.solr.services.configuration.interface.ISolrConfig"
      component=".path-to-your-module.provide_solr_config"
      />

</configure>

```

Then you can add the utility provider to your own module, and provide the configuration value as needed:

```py
def provide_solr_config():
    return {
        "fieldList": [
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
            "image_field",
            'my_extra_field_1'
        ],
        "searchTabs": [
            {
                "label": "All",
                "filter": "Type(*)"
            },
            {
                "label": "Pages",
                "filter": "Type:(Page)"
            },
            {
                "label": "More",
                "filter": "MY-SOLR-CONDITION"
            }
        ]
    }
```

# Using the solr endpoint

The solr endpoint is used from the `volto-solr` addon package for the implementation of the site search. It can also be used for custom components. The parameters roughly follow the parameters of the normal site search service, but differ in some respects.

TBD give more information about this.

For now, please refer to the source code of the `solr.py` module, in case you want to use for your own purposes.
