# Changelog

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->

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
