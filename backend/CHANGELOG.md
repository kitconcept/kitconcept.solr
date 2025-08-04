# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

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
