# Instructions for using this package

This file covers some use cases and describes the steps to support them with the kitconcept.solr package. Follow these steps to the detail, in case you encounter one of the use cases.

## Use cases overview

There are two approaches for displaying human-readable labels in facet conditions when a field stores keys or references instead of display values:

**Vocabulary support** — Use this when a field references a key from a Plone vocabulary (static or dynamic). The vocabulary is fetched by the frontend and used to look up labels for each key. Example: a `location_reference` field stores UUIDs of referenced location objects, and a dynamic vocabulary maps these UUIDs to location names.

**Calculated fields** — Use this when you need to index a computed value directly into Solr. This is more versatile: it can resolve referenced objects, compute values on the fly, or replicate what a vocabulary does by storing the resolved value at index time. Key advantages over vocabulary support are **sortability** (since the resolved value is stored in Solr, alphabetic sorting works correctly) and **search prefix filtering** (the condition field's text filter works because Solr can filter on the actual display values). Example: a `department_name` field that resolves the department name from a reference at index time, so Solr can sort results alphabetically by department.

In summary: prefer vocabulary support for straightforward key-to-label mappings. Use calculated fields when you need sortability, search prefix filtering in condition fields, or when the value comes from a complex computation or a referenced object.

---

# Using vocabulary support in facet conditions

Vocabulary support allows facet conditions to display human-readable labels instead of raw vocabulary keys. The vocabulary is fetched by the frontend from Plone's vocabulary API and used to look up the label for each facet value.

Use Case 1: A value from a dynamic vocabulary. Example: `department` is a dynamic vocabulary. We want to use the vocabulary value in the facet condition, for example `Accounting`. Without this, the vocabulary key would be used, which is not very useful.

Use Case 2: A value from a referenced object. Example: `location_reference` stores UUIDs of referenced location objects. A dynamic vocabulary maps these UUIDs to human-readable names like `"Zurich"`, `"Bern"`. For this to work, you need to implement a dynamic vocabulary that resolves the referenced objects to their display values, update the vocabulary when the referenced content changes, and consider caching the vocabulary results for performance.

Example we use below: A `location_reference` field stores UUIDs of referenced location objects (e.g., `a3f2b8c1-...`, `d7e4f9a2-...`). A dynamic vocabulary `mypackage.vocabularies.locations` maps these UUIDs to human-readable names like `"Zurich"`, `"Bern"`. With vocabulary support, the facet shows the location names instead of the UUIDs.

## 1. Add the field to the Solr schema

Add the field to the Solr schema in the `solr/etc/conf/schema.xml` file:

```xml
<field name="location_reference" type="string" indexed="true" stored="true" />
```

For facet fields, use `string` type to ensure exact value matching. Use `stored="true"` so the field is returned in search results, and `indexed="true"` so Solr can filter on it.

## 2. Configure the field with a vocabulary in the kitconcept.solr registry

In the `kitconcept.solr.interfaces.IKitconceptSolrSettings.xml` registry file, add the field to `fieldList` with its vocabulary reference:

```json
    "fieldList": [
        // ... other fields ...
        {
            "name": "location_reference",
            "vocabulary": {
                "name": "mypackage.vocabularies.locations",
                "isMultilingual": false
            }
        }
    ],
```

The vocabulary configuration has two properties:

- `name` (required): The Plone vocabulary name (as registered in the vocabulary registry).
- `isMultilingual` (optional, default: `true`): Set to `false` if the vocabulary does not have language-specific translations (e.g., technical codes, status values). When `true`, the vocabulary is fetched with the current language as a subrequest.

Then use this field as the facet field in `searchTabs`:

```json
    "searchTabs": [
        {
            "label": "Locations",
            "filter": "Type:(Location)",
            "facetFields": [
                {
                    "name": "location_reference",
                    "label": "Location"
                }
            ]
        }
    ]
```

That's it for basic vocabulary support. The backend will include the vocabulary metadata in the search response, and the frontend will automatically fetch the vocabulary and display labels in the facet conditions.

## Using useVocab in a result type template

If you have a custom result type template (e.g., `PersonResultItem`) and need to display a vocabulary label for a field in the search result, you can use the `useVocab` hook directly. The raw field value in the search result will contain the vocabulary key (e.g., a UUID), not the label, so you need to look it up programmatically.

```jsx
import { useVocab } from '../vocabs/useVocab';

const PersonResultItem = ({ item }) => {
  const vocabItems = useVocab({
    name: 'mypackage.vocabularies.locations',
    isMultilingual: false,
  });

  const locationLabel =
    vocabItems.find((v) => v.value === item.extras.location_reference)?.label ||
    item.extras.location_reference;

  return (
    <article className="tileItem personResultItem">
      <div className="itemContent">
        <h2>{item.title}</h2>
        <p>Location: {locationLabel}</p>
      </div>
    </article>
  );
};
```

The `useVocab` hook returns an array of `{ value, label }` items. Use `find` to look up the label for a given key.

If the list of vocabularies to fetch is dynamic, use the `useVocabs` hook instead. Since React requires hooks to be called unconditionally (not inside loops or conditions), `useVocabs` allows fetching a dynamic number of vocabularies with a single hook call. It takes an array of options and returns an object keyed by vocabulary name:

```jsx
import { useVocabs } from '../vocabs/useVocab';

const vocabData = useVocabs([
  { name: 'mypackage.vocabularies.locations', isMultilingual: false },
  { name: 'mypackage.vocabularies.departments', isMultilingual: true },
]);
// vocabData['mypackage.vocabularies.locations'] → [{ value, label }, ...]
// vocabData['mypackage.vocabularies.departments'] → [{ value, label }, ...]
```

### VocabContext and caching

The `useVocab` and `useVocabs` hooks require a `VocabContext` to be present in the component tree. The `VocabContext` tracks which vocabularies have already been requested and ensures each vocabulary is only fetched once (per language, for multilingual vocabularies). The `SolrSearch` component already wraps the entire search UI (sidebar and results) with a `VocabProvider`, so you do not need to add one yourself.

The `VocabContext` provides the following API:

- `isVocabRequested(name, subrequest)` — Returns `true` if the vocabulary has already been requested. The `subrequest` parameter is the language code for multilingual vocabularies, or `undefined` for unilingual ones.
- `setVocabRequested(name, subrequest)` — Marks a vocabulary as requested, preventing duplicate fetches.
- `resetContext()` — Clears the entire cache, causing all vocabularies to be re-fetched on next use. This can be used to programmatically invalidate the cache, e.g., after a vocabulary has been updated.

These methods are available via `useContext(VocabContext)`.

Normally, you don't need to use `resetContext` — vocabularies are cached until a hard page reload, which is appropriate for most use cases.

However, if you need finer control — for example, if it is really important to update the vocabularies immediately after they have been modified — you can call `resetContext()` to invalidate the cache and trigger a re-fetch. Note that `resetContext` must be called from inside the `VocabContext`, i.e., from a component that is a descendant of `VocabProvider`. Since the `VocabProvider` wraps the search component, this works for any component within the search UI. If you need to call it from outside the search component, you would need to customize the search component, remove the `VocabProvider` from it, and move it higher up in your component hierarchy.

```jsx
import { useContext } from 'react';
import { VocabContext } from '../vocabs/VocabContext';

const MyComponent = () => {
  const { resetContext } = useContext(VocabContext);
  // Call resetContext() to invalidate the vocabulary cache
};
```

## Caveat 1: alphabetic sorting

When using vocabulary support, Solr stores and sorts by the raw vocabulary keys (e.g., UUIDs), not by the display labels. This means that alphabetic sorting by a vocabulary-backed field will not produce meaningful results.

If you need correct alphabetic sorting by the display value, use calculated fields instead. With calculated fields, the resolved value is stored directly in Solr, so sorting works as expected.

## Caveat 2: search prefix box in condition fields

The search prefix box (text filter) in condition fields is not supported for vocabulary-backed fields. The prefix filtering is performed by Solr on the raw indexed values, but Solr does not know the vocabulary labels — it only stores the raw keys (e.g., UUIDs). Client-side filtering is not supported because of inefficiency with large vocabularies.

## Troubleshooting

### Facet shows raw keys (UUIDs) instead of labels

1. **Check the vocabulary is configured in `fieldList`**: The field entry must be an object with a `vocabulary` property, not a plain string.
2. **Check the vocabulary name is correct**: The `name` in the vocabulary config must match the registered Plone vocabulary name exactly.
3. **Check the vocabulary returns matching keys**: The `value` property of each vocabulary item must match the raw values stored in Solr. You can verify this by querying the vocabulary API directly: `GET /@vocabularies/mypackage.vocabularies.locations`.
4. **Check the `isMultilingual` setting**: If the vocabulary is unilingual but `isMultilingual` is `true` (the default), the hook will fetch with a language subrequest and may not find the vocabulary items. Set `isMultilingual: false` for unilingual vocabularies.

### Facet values are empty or missing

1. **Check the field exists in Solr**: Verify the field is in `schema.xml` and the Solr image has been rebuilt.
2. **Check the field is in `fieldList`**: The field must be listed in `fieldList` for it to be returned by the search endpoint.
3. **Check the content is indexed**: The field must have values indexed in Solr. Query the Solr admin interface to verify.

### Vocabulary labels not updating after changes

The `VocabContext` caches which vocabularies have been requested. If the vocabulary content changes (e.g., new items added), the cached state may prevent a re-fetch. Call `resetContext()` to invalidate the cache, or reload the page.

### Debugging tips

To verify the vocabulary is correctly returned by the backend, check the search endpoint response:

1. Open the browser developer tools, Network tab.
2. Perform a search and find the `@solr` request.
3. In the response JSON, check the `vocabularies` array — it should contain an entry for your field with the correct vocabulary name.

To verify the vocabulary itself returns correct data:

1. Query the Plone vocabulary API directly: `GET /plone/@vocabularies/mypackage.vocabularies.locations`
2. Check that each item has a `value` matching what Solr stores, and a `label` with the display text.

To debug the frontend hooks, add a temporary log in your component:

```jsx
const vocabItems = useVocab({
  name: 'mypackage.vocabularies.locations',
  isMultilingual: false,
});
console.log('vocabItems', vocabItems);
```

If vocabItems is an empty array, the vocabulary has not been fetched yet or the name doesn't match a registered vocabulary.

## Complete checklist

- [ ] Added field to Solr `schema.xml`
- [ ] Added field with vocabulary to `fieldList` in kitconcept.solr config
- [ ] Added field to `facetFields` in searchTabs config
- [ ] Ensured the Plone vocabulary is registered and returns the correct key/label pairs
- [ ] Rebuilt the Solr image (if schema.xml changed)
- [ ] Reindexed Solr with `make solr-activate-and-reindex`

---

# Using calculated fields in facet conditions

A calculated field is a content type field that is not stored in the object, but calculated on the fly.

Use Case 1: Any calculated field that is not stored in the object, but calculated on the fly. Example: in the Person object type, we want to use the `address` field, but the address is not stored in the object as a single value, but calculated on the fly.

Use Case 2: A value from a dynamic vocabulary. Example: `department` is a dynamic vocabulary. We want to use the vocabulary value in the facet condition, for example `Accounting`. Without this, the vocabulary key would be used, which is not very useful. Note: using vocabulary support (see above) is typically a better option for this use case, as it avoids the need for an indexer and reindexing.

Use Case 3: A value from a referenced object. Example: `location` is a reference to a location object. Inside the location object there is a field `name` that we want to use in the facet condition. Without this, the object's UUID would be used, which is not very useful. Note: using vocabulary support (see above) is typically a better option for this use case.

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
