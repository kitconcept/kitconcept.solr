# Change log

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->
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
