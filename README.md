# kitconcept Solr 🚀

[![Built with Cookieplone](https://img.shields.io/badge/built%20with-Cookieplone-0083be.svg?logo=cookiecutter)](https://github.com/plone/cookieplone-templates/)
[![CI](https://github.com/kitconcept/kitconcept.solr/actions/workflows/main.yml/badge.svg)](https://github.com/kitconcept/kitconcept.solr/actions/workflows/main.yml)

An opinionated Solr integration for Plone.

This repository contains the 2.x version of the following packages:

| Package | Description |
| --- | --- |
| kitconcept.solr | Backend package |
| @kitconcept/volto-solr | Volto frontend package |

**If you are looking for the 1.x version of kitconcept.solr check the [1.x branch](https://github.com/kitconcept/kitconcept.solr/tree/1.x)**

## Quick Start 🏁

### Prerequisites ✅

- An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
- [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
- [nvm](https://6.docs.plone.org/install/create-project-cookieplone.html#nvm)
- [Node.js and pnpm](https://6.docs.plone.org/install/create-project.html#node-js) 22
- [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
- [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
- [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1. Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:kitconcept/kitconcept.solr.git
    cd kitconcept.solr
    ```

2. Install this code base.

    ```shell
    make install
    ```

### Fire Up the Servers 🔥

1. Create a new Plone site on your first run.

    ```shell
    make backend-create-site
    ```

2. Start the backend at <http://localhost:8080/>.

    ```shell
    make backend-start
    ```

3. In a new shell session, start the frontend at <http://localhost:3000/>.

    ```shell
    make frontend-start
    ```

Voila! Your Plone site should be live and kicking! 🎉

### Local Stack Deployment 📦

Deploy a local Docker Compose environment that includes the following.

- Docker images for Backend and Frontend 🖼️
- A stack with a Traefik router and a PostgreSQL database 🗃️
- Accessible at [http://kitconcept.solr.localhost](http://kitconcept.solr.localhost) 🌐

Run the following commands in a shell session.

```shell
make stack-create-site
make stack-start
```

And... you're all set! Your Plone site is up and running locally! 🚀

## Project structure 🏗️

This monorepo consists of the following distinct sections:

- **backend**: Houses the API and Plone installation, utilizing pip instead of buildout, and includes a policy package named kitconcept.solr.
- **frontend**: Contains the React (Volto) package.
- **devops**: Encompasses Docker stack, Ansible playbooks, and cache settings.
- **docs**: Scaffold for writing documentation for your project.
- **solr**: Base SOLR image to be used in Plone projects.

### Why this structure? 🤔

- All necessary codebases to run the site are contained within the repository (excluding existing add-ons for Plone and React).
- Specific GitHub Workflows are triggered based on changes in each codebase (refer to .github/workflows).
- Simplifies the creation of Docker images for each codebase.
- Demonstrates Plone installation/setup without buildout.

## Code quality assurance 🧐

To check your code against quality standards, run the following shell command.

```shell
make check
```

### Format the codebase

To format and rewrite the code base, ensuring it adheres to quality standards, run the following shell command.

```shell
make format
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Python code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | `zpretty` | XML and ZCML formatting  | -- |
| frontend | ESLint | Fixes most common frontend issues | [`frontend/.eslintrc.js`](.frontend/.eslintrc.js) |
| frontend | prettier | Format JS and Typescript code  | [`frontend/.prettierrc`](.frontend/.prettierrc) |
| frontend | Stylelint | Format Styles (css, less, sass)  | [`frontend/.stylelintrc`](.frontend/.stylelintrc) |

Formatters can also be run within the `backend` or `frontend` folders.

### Linting the codebase

or `lint`:

 ```shell
make lint
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Checks code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | Pyroma | Checks Python package metadata  | -- |
| backend | check-python-versions | Checks Python version information  | -- |
| backend | `zpretty` | Checks XML and ZCML formatting  | -- |
| frontend | ESLint | Checks JS / Typescript lint | [`frontend/.eslintrc.js`](.frontend/.eslintrc.js) |
| frontend | prettier | Check JS / Typescript formatting  | [`frontend/.prettierrc`](.frontend/.prettierrc) |
| frontend | Stylelint | Check Styles (css, less, sass) formatting  | [`frontend/.stylelintrc`](.frontend/.stylelintrc) |

Linters can be run individually within the `backend` or `frontend` folders.

## Internationalization 🌐

Generate translation files for Plone and Volto with ease:

```shell
make i18n
```

## API Reference

### `@solr` Service

The `@solr` service provides full-text search capabilities via Solr.

**Endpoint:** `GET /@solr`

#### Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `q` | string | Search query. If empty or omitted, returns all results. |
| `start` | integer | Offset for pagination (0-based). |
| `rows` | integer | Number of results to return. |
| `sort` | string | Solr sort parameter (e.g., `Title asc`). |
| `group_select` | integer | Index of the search tab/filter group to use (0-based). Defaults to 0 if filters are configured. |
| `portal_type` | string[] | Filter by portal type(s). |
| `path_prefix` | string | Restrict search to a specific path. Use trailing `/` to exclude the folder itself. |
| `lang` | string | Filter by language code. Mutually exclusive with `is_multilingual`. |
| `is_multilingual` | boolean | Search across all language folders (default: `true` unless `lang` is specified). |
| `facet_conditions` | string | Base64-encoded JSON for facet filtering. |
| `extra_conditions` | string | Base64-encoded JSON for date-range and string filters. |
| `spellcheck` | boolean | Enable spellcheck suggestions (`true`/`false`). Default: `false`. |
| `collate` | boolean | Enable "did you mean" corrections when no results found (`true`/`false`). Requires `spellcheck=true`. |
| `keep_full_solr_response` | boolean | Include full Solr response data including `facet_counts` and `highlighting` (default: `false`). |

#### Example Request

```bash
curl "http://localhost:8080/Plone/@solr?q=chomsky&group_select=0&rows=10"
```

#### Example Response

```json
{
  "response": {
    "numFound": 3,
    "start": 0,
    "docs": [
      {
        "UID": "abc123",
        "Title": "My Document about Noam Chomsky",
        "Description": "An article about linguistics",
        "Type": "Page",
        "path_string": "/plone/mydocument",
        "highlighting": ["...about <em>Noam Chomsky</em>..."]
      }
    ]
  },
  "portal_path": "/plone",
  "facet_groups": [
    ["All", 3],
    ["Pages", 1],
    ["Events", 0],
    ["Images", 1],
    ["Files", 0]
  ],
  "facet_fields": [
    [{"name": "Subject", "label": "Keywords"}, [["linguistics", 2], ["science", 1]]]
  ],
  "layouts": null
}
```

#### Extra Conditions Format

The `extra_conditions` parameter accepts a base64-encoded JSON array of conditions:

```python
import base64
import json

# Date range filter
conditions = [
    ["start", "date-range", {"ge": "2021-01-01T00:00:00Z", "le": "2021-12-31T23:59:59Z"}]
]

# String filter (match any of the values)
conditions = [
    ["searchwords", "string", {"in": ["term1", "term2"]}]
]

encoded = base64.b64encode(json.dumps(conditions).encode()).decode()
```

Date range operators:

- `ge`: Greater than or equal (inclusive)
- `le`: Less than or equal (inclusive)
- `gr`: Greater than (exclusive)
- `ls`: Less than (exclusive)

---

### `@solr-suggest` Service

The `@solr-suggest` service provides autocomplete suggestions.

**Endpoint:** `GET /@solr-suggest`

#### Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `query` | string | Search term for suggestions. |
| `lang` | string | Filter by language code. Mutually exclusive with `is_multilingual`. |
| `is_multilingual` | boolean | Search across all language folders (default: `true` unless `lang` is specified). |

#### Example Request

```bash
curl "http://localhost:8080/Plone/@solr-suggest?query=chomsky"
```

#### Example Response

```json
{
  "suggestions": [
    {
      "@id": "http://localhost:8080/plone/mydocument",
      "@type": "Document",
      "title": "My Document about Noam Chomsky",
      "description": "",
      "review_state": "published",
      "type_title": "Page"
    },
    {
      "@id": "http://localhost:8080/plone/mynews",
      "@type": "News Item",
      "title": "My News Item with Noam Chomsky",
      "description": "",
      "review_state": "published",
      "type_title": "News Item"
    }
  ]
}
```

---

## Configuration

### Registry Settings

The `kitconcept.solr.config` registry record controls the behavior of the `@solr` service. It is a JSON object with the following structure:

```json
{
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
    "location",
    "contact_email",
    "contact_phone",
    "image_scales",
    "image_field"
  ],
  "highlightingFields": [
    {"field": "content", "prop": "highlighting"},
    {"field": "Title", "prop": "highlighting_title"},
    {"field": "Description", "prop": "highlighting_description"}
  ],
  "searchTabs": [
    {
      "label": "All",
      "filter": "Type(*)"
    },
    {
      "label": "Pages",
      "filter": "Type:(Page)",
      "facetFields": [
        {"name": "Subject", "label": "Keywords"}
      ],
      "layouts": ["listing", "grid"]
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
}
```

#### Configuration Options

| Property | Type | Description |
| --- | --- | --- |
| `fieldList` | string[] | Solr fields to include in search results. |
| `highlightingFields` | object[] | Fields for search term highlighting. Each object has `field` (Solr field name) and `prop` (property name in response). |
| `searchTabs` | object[] | Search filter tabs/groups. |

#### Search Tab Properties

| Property | Type | Description |
| --- | --- | --- |
| `label` | string | **Required.** Display label for the tab. |
| `filter` | string | Solr filter query (e.g., `Type:(Page)` or `Type:(Page OR "News Item")`). |
| `facetFields` | object[] | Facet fields for this tab. Each object has `name` (Solr field) and `label` (display label). |
| `layouts` | string[] | Available layout options for this tab. |

### Configuring via GenericSetup

Create a file `profiles/default/registry/kitconcept.solr.interfaces.IKitconceptSolrSettings.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<registry xmlns:i18n="http://xml.zope.org/namespaces/i18n"
          i18n:domain="kitconcept.solr">
  <records interface="kitconcept.solr.interfaces.IKitconceptSolrSettings"
           prefix="kitconcept.solr">
    <value key="config" purge="false">{
      "fieldList": ["UID", "Title", "Description", "Type", "path_string"],
      "searchTabs": [
        {"label": "All", "filter": "Type(*)"},
        {"label": "Pages", "filter": "Type:(Page)"}
      ]
    }</value>
  </records>
</registry>
```

---

## Solr Stack Setup

### Using the Docker Image

This repository provides a Solr Docker image preconfigured for Plone at `ghcr.io/kitconcept/solr`.

#### Docker Compose Example

```yaml
services:
  solr:
    image: ghcr.io/kitconcept/solr:latest
    ports:
      - "8983:8983"
    command:
      - solr-precreate
      - plone
      - /plone-config
    environment:
      SOLR_MODULES: extraction
      SOLR_OPTS: "-Dsolr.tika.url=http://tika:9998"

  tika:
    image: apache/tika:3.2.3.0-full
    ports:
      - "9998:9998"

  backend:
    image: your-plone-backend:latest
    environment:
      COLLECTIVE_SOLR_HOST: solr
      COLLECTIVE_SOLR_PORT: 8983
      COLLECTIVE_SOLR_BASE: /solr/plone
    depends_on:
      - solr
```

### Building Custom Solr Image

To customize the Solr configuration, extend the base image:

```dockerfile
FROM ghcr.io/kitconcept/solr:latest

# Copy custom configuration
COPY my-schema.xml /plone-config/conf/schema.xml
COPY my-solrconfig.xml /plone-config/conf/solrconfig.xml
```

### Environment Variables

Configure the Plone backend to connect to Solr using these environment variables:

| Variable | Description | Example |
| --- | --- | --- |
| `COLLECTIVE_SOLR_HOST` | Solr hostname | `solr` |
| `COLLECTIVE_SOLR_PORT` | Solr port | `8983` |
| `COLLECTIVE_SOLR_BASE` | Solr core path | `/solr/plone` |

### Solr Configuration Files

The Solr configuration is located in `solr/etc/conf/`:

| File | Description |
| --- | --- |
| `schema.xml` | Defines Solr fields and field types. |
| `solrconfig.xml` | Configures Solr request handlers, spellcheck, and suggest. |
| `synonyms.txt` | Synonym mappings for search. |
| `stopwords.txt` | Common words to ignore in search. |
| `mapping-FoldToASCII.txt` | Character folding for diacritics. |

---

## Credits and acknowledgements

Generated using [Cookieplone (0.9.7)](https://github.com/plone/cookieplone) and [cookieplone-templates (4d55553)](https://github.com/plone/cookieplone-templates/commit/4d55553d61416df56b3360914b398d675b3f72a6) on 2025-07-22 19:22:17.276266. A special thanks to all contributors and supporters!
