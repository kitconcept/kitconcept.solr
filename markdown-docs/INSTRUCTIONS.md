# Instructions for using this package

This file covers some use cases and describes the steps to support them with the kitconcept.solr package. Follow these steps to the detail, in case you encounter one of the use cases.

# Using calculated fields in facet conditions

A calculated field is a content type field that is not stored in the object, but calculated on the fly.

Use Case 1: A value from a referenced object. Example: `location` is a reference to a location object. Inside the location object there is a field `name` that we want to use in the facet condition. Without this, the object's UUID would be used, which is not very useful.

Use Case 2: A value from a dynamic vocabulary. Example: `department` is a dynamic vocabulary. We want to use the vocabulary value in the facet condition, for example `Accounting`. Without this, the vocabulary key would be used, which is not very useful.

Use Case 3: Any calculated field that is not stored in the object, but calculated on the fly.

Example we use below: in the Person object type, we want to use the `address` field, but the address is not stored in the object as a single value, but calculated on the fly.

Follow these steps to support this use case. If some steps are missing, the use case might fail without an error message, as Solr will gracefully fallback to None in case of missing values.

## 1. Add a Zope indexer for the field

Create a new file in the `indexers` folder, named `person.py`.

```python
from plone.indexer import indexer
from person.interfaces import IPerson

def calculate_address(context):
    # Calculate the address from the context
    return "123 Main St, Anytown, USA"

@indexer(IPerson)
def address_indexer(context):
    return calculate_address(context)
```

Then register the indexer in the `configure.zcml` file:

```xml
<configure xmlns="http://namespaces.zope.org/zope">
    <adapter factory=".person.address_indexer" name="address" />
</configure>
```

## 2. Add the field as a Zope catalog column

Add the field as a column value in the `catalog.xml` file:

```xml
<?xml version="1.0" encoding="utf-8"?>
<object name="portal_catalog">
  <column value="address" />
</object>
```

There is no need to add an actual catalog index, because you won't search on this field through the Zope catalog. The column (metadata) is used by collective.solr to retrieve the value during reindexing.

## 3. Add the field to the Solr schema

Add the field to the Solr schema in the `solr/etc/conf/schema.xml` file:

```xml
<field name="address" type="string" indexed="true" stored="true" />
```

Field type options:

- `string`: Exact match (good for facets and filters)
- `text`: Full-text searchable (tokenized, analyzed)
- `strings`: Multi-valued exact match

For facet fields, use `string` type to ensure exact value matching.

You need to use `stored="true"` to ensure the field is returned as a result of a search. In addition, you need to use `indexed="true"` to ensure the field is indexed and searchable by Solr.

## 4. Update the kitconcept.solr registry

In the `kitconcept.solr.interfaces.IKitconceptSolrSettings.xml` registry file, add the field to the `fieldList`. This is needed for the field to be returned as a result of a search.

```json
    "fieldList": [
        // ... other fields ...
        "address"
    ],
```

Then use this field as the facet field:

```json
    "searchTabs": [
        {
            "label": "Persons",
            "filter": "Type:(Person)",
            "facetFields": [
                {
                    "name": "address",
                    "label": "Address"
                }
            ]
        }
    ]
```

## 5. Add a site upgrade step

Add to `upgrades/configure.zcml` file:

```xml
<genericsetup:upgradeSteps
      profile="your.package:default"
      source="20260126001"
      destination="20260126002"
      >
    <genericsetup:upgradeDepends
        title="Add address index to the catalog"
        import_steps="catalog"
        />
    <genericsetup:upgradeStep
        title="Reindex Person type"
        handler=".catalog.reindex_person_type"
        />
</genericsetup:upgradeSteps>
```

Add a script to reindex the Person type in the `catalog.py` file:

```python
from logging import getLogger
from plone import api
from Products.ZCatalog.Catalog import CatalogError

import transaction


logger = getLogger(__name__)


def reindex_type(context, portal_type: str, idxs=[], update_metadata=1):
    catalog = api.portal.get_tool("portal_catalog")
    i = 0
    for i, brain in enumerate(
        catalog.unrestrictedSearchResults(portal_type=portal_type)
    ):
        try:
            obj = brain._unrestrictedGetObject()
            catalog.catalog_object(obj, idxs=idxs, update_metadata=update_metadata)
        except CatalogError:
            logger.error(f"Error reindexing {brain.getPath()}")
            raise

        # Commit every 1000 objects
        if i and not i % 1000:
            logger.info(f"Commit checkpoint at {i} items of type {portal_type}")
            transaction.commit()

    transaction.commit()
    logger.info(f"Reindexed {i} items of type {portal_type}")

def reindex_person_type(context):
    reindex_type(context, "Person")
```

Update `metadata.xml` to contain the new version number - update from 20260126001 to 20260126002.

## 6. Rebuild the Solr image and reindex Solr

You must rebuild the Solr image to make the new `schema.xml` configuration take effect.

After rebuilding the Solr image, you need to reindex Solr.

```bash
make solr-activate-and-reindex
```

## 7. Execute the site upgrade step

Execute the site upgrade step to apply the changes. This will update the catalog columns and reindex the content type.

## Troubleshooting

### Field shows None values in facets

If your facet field shows `None` instead of the calculated values:

1. **Check the indexer is registered**: Verify the adapter is correctly registered in `configure.zcml`
2. **Check the catalog column exists**: Go to `portal_catalog` in ZMI and verify the column is listed
3. **Check the Solr schema**: Verify the field exists in `schema.xml`
4. **Check the Solr image is rebuilt**: The Solr image must be rebuilt after modifying `schema.xml`
5. **Reindex the content**: The content needs to be reindexed after adding the indexer

### Field not appearing in search results

If the field doesn't appear in search results:

1. **Check the fieldList**: Verify the field is added to `fieldList` in the kitconcept.solr config
2. **Check Solr schema**: Ensure `stored="true"` is set for the field in `schema.xml`

### Debugging tips

You can check if a field is correctly indexed in Solr by:

1. Going to the Solr admin interface (usually `http://localhost:8983/solr`)
2. Selecting the core and check if the image is rebuilt with this configuration (under Documents)
3. Selecting the core and running a query
4. Checking if the field appears in the document

To verify the indexer works correctly, you can test in Python:

```python
from plone.indexer.interfaces import IIndexer
from zope.component import getAdapter

obj = context  # Your Person object
indexer = getAdapter(obj, IIndexer, name='address')
print(indexer())
```

## Complete checklist

Use this checklist to ensure all steps are completed:

- [ ] Created indexer function in `indexers/` folder
- [ ] Registered indexer adapter in `configure.zcml`
- [ ] Added column to `catalog.xml`
- [ ] Added field to Solr `schema.xml`
- [ ] Added field to `fieldList` in kitconcept.solr config
- [ ] Added field to `facetFields` in searchTabs config
- [ ] Created upgrade step to reindex content
- [ ] Rebuilt the Solr image
- [ ] Reindexed Solr with `make solr-activate-and-reindex`
- [ ] Ran the site upgrade step
