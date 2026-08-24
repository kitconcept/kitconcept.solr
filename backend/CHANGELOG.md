# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 3.0.0a0 (2026-08-24)


### New features:

- Support the new Volto editor's (Plate) block storage in the RAG chunking - both kinds of pages coexist in the same site. @reebalazs [#79](https://github.com/kitconcept/kitconcept-solr/issues/79)
- Ship the German RAG test corpus as a plone.exportimport dump in setuphandlers/examplecontent (curated export of the fictional intranet demo site: 409 objects, 80 images, 7 example users), with an import-example-content make target, an importer script that skips uninstalled portal types, and a SITE_DEFAULT_LANGUAGE option for create-site. @reebalazs [#79](https://github.com/kitconcept/kitconcept-solr/issues/79)
- Hybrid retrieval for the RAG search: parent-level Reciprocal Rank Fusion of the knn chunk ranking with the classic keyword query (an exact copy of the @solr main query incl. searchwords boost and showinsearch exclusion); prompt context labeled by document title instead of leaking bracketed reference numbers. @reebalazs [#79](https://github.com/kitconcept/kitconcept-solr/issues/79)
- Add the @rag-search endpoint: single-turn RAG search on a query pipeline (embed, permission-trimmed knn chunk retrieval, parent collapse, grounded answer generation) with structured error results. Exclude Image content from chunking. @reebalazs [#79](https://github.com/kitconcept/kitconcept-solr/issues/79)
- Suggest: support the ``extra_conditions`` filter parameter - the same
  mechanism and encoding as the ``@solr`` endpoint - so livesearch
  consumers can filter by type, creator, modification date or review
  state. An explicit type filter wins over the built-in type exclusion
  list. @reebalazs [#121](https://github.com/kitconcept/kitconcept-solr/issues/121)


### Bug fixes:

- RAG: strip the model's reasoning also when the completion contains only a
  closing ``</think>`` tag (some model templates consume the opening tag,
  observed with qwen3:4b via Ollama), so chain-of-thought is never shown to
  users. @reebalazs [#79](https://github.com/kitconcept/kitconcept-solr/issues/79)
- RAG: fix Plate chunking, by extracting text also from blocks that are not listed in
  ``blocks_layout`` @reebalazs [#112](https://github.com/kitconcept/kitconcept-solr/issues/112)

## 2.0.0 (2026-08-22)


### Bug fixes:

- Suggest: pass `include_expansion=False` when serializing a suggestion in full, so the `@components` expansion links are not embedded into the type-ahead response. @reebalazs [#114](https://github.com/kitconcept/kitconcept-solr/issues/114)

## 2.0.0rc0 (2026-08-14)


### Bug fixes:

- @solr-suggest accepts an optional path_prefix (path_parents filter), so livesearch suggestions honor a subtree scope like the search results do. @reebalazs [#101](https://github.com/kitconcept/kitconcept-solr/issues/101)
- Suggest: pass `include_items=False` when serializing a suggestion in full. For folderish portal types plone.restapi would otherwise run an extra catalog query per suggestion and embed the entire child listing into the type-ahead response. @reebalazs [#105](https://github.com/kitconcept/kitconcept-solr/issues/105)


### Internal:

- The backend test suite runs ~8.5x faster (7:27 -> 0:53): the Plone test layers stay alive for the whole pytest session instead of being rebuilt per test class, and content creation plus the Solr query of a parametrized test class run once per class instead of once per assertion. @reebalazs [#81](https://github.com/kitconcept/kitconcept-solr/issues/81)
- The test Solr/Tika containers use ephemeral host ports: the tests never touch (nor get blocked by) a locally running site Solr on 8983, and a dev site and the test suite can run at the same time. @reebalazs [#83](https://github.com/kitconcept/kitconcept-solr/issues/83)
- Fix three RUF005 lint violations in the navigation tests that were invisible to CI (the shared lint workflow's `ruff check --diff` only reports violations with a safe autofix). @reebalazs 

## 2.0.0a14 (2026-06-10)

No significant changes.


## 2.0.0a13 (2026-03-19)


### New features:

- Add vocabulary support for facet conditions. @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issues/63)


### Bug fixes:

- Fix test_services_navigation.py which used the wrong layer and corrupted ZODB state @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issues/63)

## 2.0.0a12 (2026-02-10)


### New features:

- Add @navigation_with_excluded service for breadcrumbs that includes items excluded from navigation @reebalazs 

## 2.0.0a11 (2026-02-09)

No significant changes.


## 2.0.0a10 (2026-02-08)


### New features:

- Add support for spelling suggestions and collations ("Did you mean ___?") @reebalazs 
- In search results, highlight search terms in both title and description @reebalazs 
- Make it possible to override the SolrSearchWidget component by setting config.widgets.SolrSearchWidget @reebalazs 


### Bug fixes:

- Fix filtering by multiple facet conditions failing to correctly disable voided conditions. @reebalazs 

## 2.0.0a9 (2026-01-22)

No significant changes.


## 2.0.0a8 (2025-12-10)


### Bug fixes:

- Enable the `use_tika` setting from `collective.solr` to make sure text can be extracted from binary files with recent versions of Solr. @reebalazs 

## 2.0.0a7 (2025-12-01)


### Internal:

- Fix repository URL in package metadata. @davisagli 

## 2.0.0a6 (2025-11-20)


### Bug fixes:

- Fix suggestion service @reebalazs 

## 2.0.0a5 (2025-11-11)

No significant changes.


## 2.0.0a4 (2025-11-11)

No significant changes.


## 2.0.0a3 (2025-09-22)

No significant changes.


## 2.0.0a2 (2025-09-04)


### New features:

- Add support for an autocomplete livesearch widget @reebalazs [#28](https://github.com/kitconcept/kitconcept-solr/issues/28)

## 2.0.0a1 (2025-08-04)


### New features:

- Add the value of the `collective.solr.active` setting to the REST API
  `@site` endpoint, so that the frontend can check if solr is active.
  (This doesn't do anything unless you have plone.restapi 9.14.0+)
  @davisagli [#39](https://github.com/kitconcept/kitconcept-solr/issues/39)

## 1.0.0a6 (2024-04-09)


### Bug fixes:

- Fix first tab condition @reebalazs [#26](https://github.com/kitconcept/kitconcept-solr/issues/26)


## 1.0.0a5 (2024-03-01)


### New features:

- Add support for sidebar facet conditions @reebalazs [#24](https://github.com/kitconcept/kitconcept-solr/issues/24)


### Bug fixes:

- Fix solr search security problem with individual users @reebalazs [#20](https://github.com/kitconcept/kitconcept-solr/issues/20)


## 1.0.0a5 (2024-02-01)


### Bug fixes:

- Fix generic setup profile titles @tisto [#18](https://github.com/kitconcept/kitconcept-solr/issues/18)


## 1.0.0a4 (2023-10-10)


### New features:

- Support Plone 5.2 [@reekitconcept] [#17](https://github.com/kitconcept/kitconcept-solr/issues/17)


## 1.0.0a3 (2023-08-15)


### Documentation:

- Add credits to README @tisto [#16](https://github.com/kitconcept/kitconcept-solr/issues/16)


## 1.0.0a2 (2023-08-15)


### Bug fixes:

- Increase version of collective.solr @reebalazs [#14](https://github.com/kitconcept/kitconcept-solr/issues/14)


## 1.0.0a1 (2023-08-11)


### New features:

- Generate `ghcr.io/kitconcept/solr` @reekitconcept [#3](https://github.com/kitconcept/kitconcept-solr/issues/3)


### Internal:

- Prepare package for release @ericof [#5](https://github.com/kitconcept/kitconcept-solr/issues/5)
- Revamp solr configuration @reebalazs [#12](https://github.com/kitconcept/kitconcept-solr/issues/12)
