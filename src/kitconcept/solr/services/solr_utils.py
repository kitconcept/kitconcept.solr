from plone import api
from typing import List


class SolrConfigError(RuntimeError):
    pass


class SolrConfig:
    config: dict
    filters: list

    def __init__(self):
        self.config = api.portal.get_registry_record("kitconcept.solr.config")
        search_tabs = self.config.get("searchTabs", [])
        self.filters = [item["filter"] for item in search_tabs]

    @property
    def labels(self):
        labels = list(
            map(lambda item: item.get("label", ""), self.config.get("searchTabs", []))
        )
        if len(labels) == 0:
            raise SolrConfigError(
                "Error parsing solr config, searchTabs either missing or empty"
            )
        invalid_labels = [label for label in labels if not label]
        if invalid_labels:
            raise SolrConfigError(
                "Error parsing solr config, missing label in searchTabs. Labels are mandatory."
            )
        return labels

    def select_condition(self, group_select: str) -> str:
        filters = self.filters
        base_query = "{!tag=typefilter}"
        condition = filters[group_select]
        return f"{base_query}{condition}"

    @property
    def facet_query(self) -> List[str]:
        return list(map(lambda item: "{!ex=typefilter}" + item, self.filters))

    @property
    def field_list(self) -> List[str]:
        raw_value = self.config.get("fieldList", [])
        invalid_fields = [item for item in raw_value if "," in item]
        if invalid_fields:
            raise SolrConfigError(
                "Error parsing solr config, fieldList item contains comma (,) which is prohibited"
            )
        return ",".join(raw_value)
