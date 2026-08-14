# Change log

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->
## 2.0.0rc0 (2026-08-14)

### Backend


#### Bug fixes:

- @solr-suggest accepts an optional path_prefix (path_parents filter), so livesearch suggestions honor a subtree scope like the search results do. @reebalazs [#101](https://github.com/kitconcept/kitconcept-solr/issues/101)
- Suggest: pass `include_items=False` when serializing a suggestion in full. For folderish portal types plone.restapi would otherwise run an extra catalog query per suggestion and embed the entire child listing into the type-ahead response. @reebalazs [#105](https://github.com/kitconcept/kitconcept-solr/issues/105)


#### Internal:

- The backend test suite runs ~8.5x faster (7:27 -> 0:53): the Plone test layers stay alive for the whole pytest session instead of being rebuilt per test class, and content creation plus the Solr query of a parametrized test class run once per class instead of once per assertion. @reebalazs [#81](https://github.com/kitconcept/kitconcept-solr/issues/81)
- The test Solr/Tika containers use ephemeral host ports: the tests never touch (nor get blocked by) a locally running site Solr on 8983, and a dev site and the test suite can run at the same time. @reebalazs [#83](https://github.com/kitconcept/kitconcept-solr/issues/83)
- Fix three RUF005 lint violations in the navigation tests that were invisible to CI (the shared lint workflow's `ruff check --diff` only reports violations with a safe autofix). @reebalazs 



### Frontend

#### Bugfix

- Fix React warning in SearchConditions: the useMemo dependency array grew as vocabularies loaded (spread of vocabData values); use the vocabData object itself as a constant-size dependency. @reebalazs [#94](https://github.com/kitconcept/kitconcept-solr/issue/94)
- Fix React prop-types warning on client-side navigation to the search page: the Toolbar portal is rendered as a sibling of the Segment instead of a child (prop-types does not recognize ReactPortal as a node). @reebalazs [#97](https://github.com/kitconcept/kitconcept-solr/issue/97)
- Local search fixes: @solr-suggest accepts an optional path_prefix so suggestions honor a subtree scope, and an explicit path_prefix URL param wins over the getPathPrefix heuristic, which silently dropped top-level (single-segment) prefixes. @reebalazs [#101](https://github.com/kitconcept/kitconcept-solr/issue/101)



### Project


#### Bugfix

- Remove config files from an existing Solr core when they are removed from the image. @reekitconcept [#107](https://github.com/kitconcept/kitconcept-solr/pull/107)


#### Internal

- Tag the published Solr image (`ghcr.io/kitconcept/solr`) with the release number in addition to the commit SHA, so consumers can pin the same release number for the backend, frontend and Solr image. @reebalazs [#76](https://github.com/kitconcept/kitconcept-solr/pull/76)
- The test Solr/Tika containers use ephemeral host ports (docker-compose-dev.yml mappings are parameterized): the tests never touch a locally running site Solr on 8983, and a dev site and the test suite can run at the same time. @reebalazs [#83](https://github.com/kitconcept/kitconcept-solr/pull/83)
- Stop overriding the image `CMD` with `solr-precreate` in the compose files. @reekitconcept [#107](https://github.com/kitconcept/kitconcept-solr/pull/107)
- Stop the `tika-acceptance` container when the acceptance backend is stopped. `make acceptance-backend-dev-start` now names it explicitly in `docker compose up` so Ctrl-C tears it down instead of leaving it running. @reebalazs 



## 2.0.0a14 (2026-06-10)

### Backend

No significant changes.




### Frontend

#### Bugfix

- Fix grey bars around facets in search @iRohitSingh [#75](https://github.com/kitconcept/kitconcept-solr/issue/75)
- Hide the empty search tabs container on an empty search term, so it no longer renders as a stray grey rectangle. @reebalazs 



### Project


#### Feature

- Add dense 768 dimension vector field for embeddings. @danalvrz 


#### Bugfix

- Fix `knn_vector_768` field type so the Solr core can load: use `hnswBeamWidth` instead of the unrecognized `hnswEfConstruction` attribute on `solr.DenseVectorField`. @reebalazs 


#### Internal

- Run acceptance and backend tests on `solr/**` changes, and smoke-test the built Solr image (boot it and ping the `plone` core) before pushing it. @reebalazs 



## 2.0.0a13 (2026-03-19)

### Backend


#### New features:

- Add vocabulary support for facet conditions. @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issues/63)


#### Bug fixes:

- Fix test_services_navigation.py which used the wrong layer and corrupted ZODB state @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issues/63)



### Frontend

#### Feature

- Add vocabulary support for facet conditions. @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issue/63)

#### Bugfix

- Fix useSelector rerenders in SolrSearchAutosuggest and routes @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/issue/63)
- Fix livesearch widget exception during text changes @reebalazs 



### Project


#### Feature

- Add phone, building and room fields for Person content type in schema. @danalvrz 


#### Documentation

- Add instructions for vocabulary support and calculated fields in facet conditions. @reebalazs [#63](https://github.com/kitconcept/kitconcept-solr/pull/63)



## 2.0.0a12 (2026-02-10)

### Backend


#### New features:

- Add @navigation_with_excluded service for breadcrumbs that includes items excluded from navigation @reebalazs 



### Frontend

No significant changes.


### Project

No significant changes.




## 2.0.0a11 (2026-02-09)

### Backend

No significant changes.




### Frontend

#### Bugfix

- Add missing exports in package.json to fix eslint errors in consumers @reebalazs 



### Project

No significant changes.




## 2.0.0a10 (2026-02-08)

### Backend


#### New features:

- Add support for spelling suggestions and collations ("Did you mean ___?") @reebalazs 
- In search results, highlight search terms in both title and description @reebalazs 
- Make it possible to override the SolrSearchWidget component by setting config.widgets.SolrSearchWidget @reebalazs 


#### Bug fixes:

- Fix filtering by multiple facet conditions failing to correctly disable voided conditions. @reebalazs 



### Frontend

#### Feature

- Add support for spelling suggestions and collations ("Did you mean ___?") @reebalazs 
- In search results, highlight search terms in both title and description @reebalazs 
- Make it possible to override the SolrSearchWidget component by setting config.widgets.SolrSearchWidget @reebalazs 

#### Bugfix

- Fix filtering by multiple facet conditions failing to correctly disable voided conditions. @reebalazs 



### Project


#### Feature

- Add support for spelling suggestions and collations ("Did you mean ___?") @reebalazs 
- In search results, highlight search terms in both title and description @reebalazs 
- Make it possible to override the SolrSearchWidget component by setting config.widgets.SolrSearchWidget @reebalazs 


#### Bugfix

- Fix filtering by multiple facet conditions failing to correctly disable voided conditions. @reebalazs 
- In the ghcr.io/kitconcept/solr image, make sure existing solr cores are updated with schema changes. @davisagli 



## 2.0.0a9 (2026-01-22)

### Backend

No significant changes.




### Frontend

No significant changes.


### Project


#### Feature

- Add kitconcept.intranet field to schema: responsibilities. @danalvrz 


#### Documentation

- Fix docs for configuring Tika URL. @davisagli 



## 2.0.0a8 (2025-12-10)

### Backend


#### Bug fixes:

- Enable the `use_tika` setting from `collective.solr` to make sure text can be extracted from binary files with recent versions of Solr. @reebalazs 



### Frontend

No significant changes.


### Project


#### Bugfix

- Upgrade to Solr 9.10 with external Tika server 3.2.3 to fix CVE-2025-66516.
  See docs/docs/how-to-guides/upgrade-cve-2025-66516.md for details. @reebalazs 


#### Internal

- Fix publishing of ghcr.io/kitconcept/solr image. @davisagli 



## 2.0.0a7 (2025-12-01)

### Backend


#### Internal:

- Fix repository URL in package metadata. @davisagli 



### Frontend

No significant changes.


### Project


#### Feature

- Add kitconcept.intranet fields to schema: organisational_unit_reference and location_reference. @davisagli 



## 2.0.0a6 (2025-11-20)

### Backend


#### Bug fixes:

- Fix suggestion service @reebalazs 



### Frontend

No significant changes.


### Project

No significant changes.




## 2.0.0a5 (2025-11-11)

### Backend

No significant changes.




### Frontend

#### Bugfix

- Pass in aria props to the input in SolrSearchAutosuggest @reebalazs [#pass-aria-props-to-input](https://github.com/kitconcept/kitconcept-solr/issue/pass-aria-props-to-input)

#### Internal

- Fix solr search widget inline functions @reebalazs 



### Project

No significant changes.




## 2.0.0a4 (2025-11-11)

### Backend

No significant changes.




### Frontend

#### Bugfix

- Fixed intranet header in VLT CSS leak. @sneridagh 



### Project

No significant changes.




## 2.0.0a3 (2025-09-22)

### Backend

No significant changes.




### Frontend

#### Bugfix

- Fix broken css that broke sites due to search class @reebalazs [#49](https://github.com/kitconcept/kitconcept-solr/issue/49)



### Project

No significant changes.




## 2.0.0a2 (2025-09-04)

### Backend


#### New features:

- Add support for an autocomplete livesearch widget @reebalazs [#28](https://github.com/kitconcept/kitconcept-solr/issues/28)



### Frontend

#### Feature

- Add support for an autocomplete livesearch widget @reebalazs [#28](https://github.com/kitconcept/kitconcept-solr/issue/28)



### Project


#### Internal

- Fix top level news folder. @ericof 



## 2.0.0a1 (2025-08-04)

### Backend


#### New features:

- Add the value of the `collective.solr.active` setting to the REST API
  `@site` endpoint, so that the frontend can check if solr is active.
  (This doesn't do anything unless you have plone.restapi 9.14.0+)
  @davisagli [#39](https://github.com/kitconcept/kitconcept-solr/issues/39)



### Frontend

#### Feature

- Add a `isBackendAvailable` setting to check if the Solr backend is available.
  If not, fall back to the normal Volto Search component.
  By default, this setting assumes the backend is always available.
  @davisagli [#34](https://github.com/kitconcept/kitconcept-solr/issue/34)



### Project


#### Feature

- Merge kitconcept.solr and @kitconcept/volto-solr repositories into a monorepo. @ericof 




## 1.0.0a6 (2024-04-09)

### Backend

#### Bug fixes:

- Fix first tab condition @reebalazs [#26](https://github.com/kitconcept/kitconcept-solr/issues/26)


## 1.0.0-alpha.5 (2024-04-16)

### Frontend

#### Feature

- Add support for sidebar facet conditions @reebalazs [#23](https://github.com/kitconcept/volto-solr/pull/23)

## 1.0.0a5 (2024-03-01)

### Backend
#### New features:

- Add support for sidebar facet conditions @reebalazs [#24](https://github.com/kitconcept/kitconcept-solr/issues/24)


#### Bug fixes:

- Fix solr search security problem with individual users @reebalazs [#20](https://github.com/kitconcept/kitconcept-solr/issues/20)
- Fix generic setup profile titles @tisto [#18](https://github.com/kitconcept/kitconcept-solr/issues/18)


## 1.0.0-alpha.4 (2024-03-06)

### Frontend

#### Bugfix

- Send solr request only once [#25] @reebalazs [#19](https://github.com/kitconcept/volto-solr/pull/19)

## 1.0.0a4 (2023-10-10)

### Backend

#### New features:

- Support Plone 5.2 [@reekitconcept] [#17](https://github.com/kitconcept/kitconcept-solr/issues/17)


## 1.0.0-alpha.3 (2024-03-04)

### Frontend

#### Feature

- Add support for sidebar facet conditions @reebalazs [#15](https://github.com/kitconcept/volto-solr/pull/15)

#### Bugfix

- Fix translations for the result tabs @reebalazs [#16](https://github.com/kitconcept/volto-solr/pull/16)

## 1.0.0a3 (2023-08-15)

### Backend

#### Documentation:

- Add credits to README @tisto [#16](https://github.com/kitconcept/kitconcept-solr/issues/16)

## 1.0.0-alpha.2 (2023-08-21)

### Frontend
#### Feature

- New result type icons @reekitconcept [#11](https://github.com/kitconcept/volto-solr/pull/11)


## 1.0.0a2 (2023-08-15)

### Backend

#### Bug fixes:

- Increase version of collective.solr @reebalazs [#14](https://github.com/kitconcept/kitconcept-solr/issues/14)


## 1.0.0-alpha.1 (2023-08-17)

### Frontend
#### Feature

- Add solr support @reebalazs [#2](https://github.com/kitconcept/volto-solr/pull/2)
- Revamp solr configuration, separate configuration on back-end @reebalazs [#7](https://github.com/kitconcept/volto-solr/pull/7)
- Update result type templates @reebalazs [#9](https://github.com/kitconcept/volto-solr/pull/9)
- Improved result type icons configuration @reebalazs [#10](https://github.com/kitconcept/volto-solr/pull/10)


## 1.0.0a1 (2023-08-11)

### Backend

#### New features:

- Generate `ghcr.io/kitconcept/solr` @reekitconcept [#3](https://github.com/kitconcept/kitconcept-solr/issues/3)


#### Internal:

- Prepare package for release @ericof [#5](https://github.com/kitconcept/kitconcept-solr/issues/5)
- Revamp solr configuration @reebalazs [#12](https://github.com/kitconcept/kitconcept-solr/issues/12)
