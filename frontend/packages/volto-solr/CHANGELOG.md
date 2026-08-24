# Changelog

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->

## 3.0.0-alpha.0 (2026-08-24)

### Feature

- solrSearchSuggestions accepts encoded extra conditions (new
  encodeExtraConditions helper), and the search page keeps the
  extra_conditions URL parameter across in-page interactions. @reebalazs [#121](https://github.com/kitconcept/kitconcept-solr/issue/121)
- A local (subtree) search on the search page also scopes the AI retrieval, so the answer's grounding matches the classic results: the ragSearch action takes an optional pathPrefix. @reebalazs 

## 2.0.0 (2026-08-22)

## 2.0.0-rc.0 (2026-08-14)

### Bugfix

- Fix React warning in SearchConditions: the useMemo dependency array grew as vocabularies loaded (spread of vocabData values); use the vocabData object itself as a constant-size dependency. @reebalazs [#94](https://github.com/kitconcept/kitconcept-solr/issue/94)
- Fix React prop-types warning on client-side navigation to the search page: the Toolbar portal is rendered as a sibling of the Segment instead of a child (prop-types does not recognize ReactPortal as a node). @reebalazs [#97](https://github.com/kitconcept/kitconcept-solr/issue/97)
- Local search fixes: @solr-suggest accepts an optional path_prefix so suggestions honor a subtree scope, and an explicit path_prefix URL param wins over the getPathPrefix heuristic, which silently dropped top-level (single-segment) prefixes. @reebalazs [#101](https://github.com/kitconcept/kitconcept-solr/issue/101)

## 2.0.0-alpha.14 (2026-06-10)

### Bugfix

- Fix grey bars around facets in search @iRohitSingh [#75](https://github.com/kitconcept/kitconcept-solr/issue/75)
- Hide the empty search tabs container on an empty search term, so it no longer renders as a stray grey rectangle. @reebalazs 

## 2.0.0-alpha.13 (2026-03-19)

### Feature

- Add vocabulary support for facet conditions. @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issue/63)

### Bugfix

- Fix useSelector rerenders in SolrSearchAutosuggest and routes @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issue/63)
- Fix livesearch widget exception during text changes @reebalazs 

## 2.0.0-alpha.12 (2026-02-10)

## 2.0.0-alpha.11 (2026-02-09)

### Bugfix

- Add missing exports in package.json to fix eslint errors in consumers @reebalazs 

## 2.0.0-alpha.10 (2026-02-08)

### Feature

- Add support for spelling suggestions and collations ("Did you mean ___?") @reebalazs 
- In search results, highlight search terms in both title and description @reebalazs 
- Make it possible to override the SolrSearchWidget component by setting config.widgets.SolrSearchWidget @reebalazs 

### Bugfix

- Fix filtering by multiple facet conditions failing to correctly disable voided conditions. @reebalazs 

## 2.0.0-alpha.9 (2026-01-22)

## 2.0.0-alpha.8 (2025-12-10)

## 2.0.0-alpha.7 (2025-12-01)

## 2.0.0-alpha.6 (2025-11-20)

## 2.0.0-alpha.5 (2025-11-11)

### Bugfix

- Pass in aria props to the input in SolrSearchAutosuggest @reebalazs [#pass-aria-props-to-input](https://github.com/kitconcept/kitconcept-solr/issue/pass-aria-props-to-input)

### Internal

- Fix solr search widget inline functions @reebalazs 

## 2.0.0-alpha.4 (2025-11-11)

### Bugfix

- Fixed intranet header in VLT CSS leak. @sneridagh 

## 2.0.0-alpha.3 (2025-09-22)

### Bugfix

- Fix broken css that broke sites due to search class @reebalazs [#49](https://github.com/kitconcept/kitconcept-solr/issue/49)

## 2.0.0-alpha.2 (2025-09-04)

### Feature

- Add support for an autocomplete livesearch widget @reebalazs [#28](https://github.com/kitconcept/kitconcept-solr/issue/28)

## 2.0.0-alpha.1 (2025-08-04)

### Feature

- Add a `isBackendAvailable` setting to check if the Solr backend is available.
  If not, fall back to the normal Volto Search component.
  By default, this setting assumes the backend is always available.
  @davisagli [#34](https://github.com/kitconcept/kitconcept-solr/issue/34)

## 1.0.0-alpha.5 (2024-04-16)

### Feature

- Add support for sidebar facet conditions @reebalazs [#23](https://github.com/kitconcept/volto-solr/pull/23)

## 1.0.0-alpha.4 (2024-03-06)

### Bugfix

- Send solr request only once [#25] @reebalazs [#19](https://github.com/kitconcept/volto-solr/pull/19)

## 1.0.0-alpha.3 (2024-03-04)

### Feature

- Add support for sidebar facet conditions @reebalazs [#15](https://github.com/kitconcept/volto-solr/pull/15)

### Bugfix

- Fix translations for the result tabs @reebalazs [#16](https://github.com/kitconcept/volto-solr/pull/16)

## 1.0.0-alpha.2 (2023-08-21)

### Feature

- New result type icons @reekitconcept [#11](https://github.com/kitconcept/volto-solr/pull/11)


## 1.0.0-alpha.1 (2023-08-17)

### Feature

- Add solr support @reebalazs [#2](https://github.com/kitconcept/volto-solr/pull/2)
- Revamp solr configuration, separate configuration on back-end @reebalazs [#7](https://github.com/kitconcept/volto-solr/pull/7)
- Update result type templates @reebalazs [#9](https://github.com/kitconcept/volto-solr/pull/9)
- Improved result type icons configuration @reebalazs [#10](https://github.com/kitconcept/volto-solr/pull/10)
