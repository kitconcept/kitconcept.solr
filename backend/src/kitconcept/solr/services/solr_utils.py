from plone import api

import base64
import json
import logging
import re


logger = logging.getLogger("kitconcept.solr")
logger.setLevel(logging.DEBUG)


SPECIAL_CHARS = [
    "+",
    "-",
    "&",
    "|",
    "!",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    "^",
    '"',
    "~",
    "*",
    "?",
    ":",
    "/",
]


def escape(term):
    # Backslash has to escape itself
    term = term.replace("\\", "\\\\")
    # Escape all chars in the list
    for char in SPECIAL_CHARS:
        term = term.replace(char, "\\" + char)
    return term


def replace_colon(term):
    return term.replace(":", "$")


re_replace_reserved = re.compile(r"\b(AND|OR|NOT)\b")


def replace_reserved(query):
    return re_replace_reserved.sub(lambda m: m.group(0).lower(), query)


class SolrConfigError(RuntimeError):
    pass


class SolrConfig:
    config: dict
    filters: list

    def __init__(self):
        self.config = api.portal.get_registry_record("kitconcept.solr.config")
        search_tabs = self.config.get("searchTabs", [])
        self.filters = [item["filter"] for item in search_tabs]
        self.listOflayouts = [item.get("layouts", None) for item in search_tabs]
        self.listOfFacetFields = [item.get("facetFields", []) for item in search_tabs]

    @property
    def labels(self):
        labels = [item.get("label", "") for item in self.config.get("searchTabs", [])]
        if len(labels) == 0:
            raise SolrConfigError(
                "Error parsing solr config, searchTabs either missing or empty"
            )
        invalid_labels = [label for label in labels if not label]
        if invalid_labels:
            raise SolrConfigError(
                "Error parsing solr config, missing label in searchTabs. "
                "Labels are mandatory."
            )
        return labels

    def select_condition(self, group_select: int) -> str:
        filters = self.filters
        base_query = "{!tag=typefilter}"
        condition = filters[group_select]
        return f"{base_query}{condition}"

    @property
    def field_list(self) -> str:
        raw_value = self.config.get("fieldList", [])
        invalid_fields = [item for item in raw_value if "," in item]
        if invalid_fields:
            raise SolrConfigError(
                "Error parsing solr config, fieldList item contains comma (,) "
                "which is prohibited"
            )
        return ",".join(raw_value)

    def select_layouts(self, group_select: int) -> list:
        return self.listOflayouts[group_select]

    def select_facet_fields(self, group_select: int) -> list:
        return self.listOfFacetFields[group_select]


class FacetConditions:
    config: dict
    # The limits are hardcoded ATM and limit_less MUST match the on the client.
    limit_less: int = 5
    limit_more: int = 100

    def __init__(self, config: dict):
        self.config = config

    @classmethod
    def from_encoded(cls, raw: str | None):
        if raw is not None:
            try:
                config = json.loads(base64.b64decode(raw))
            except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                logger.warning("Ignoring invalid base64 encoded string", exc_info=True)
                config = {}
        else:
            config = {}
        return cls(config)

    @staticmethod
    def value_condition(field_name: str, value: str, selected: bool):
        return (
            (f'{field_name}:"{escape(value)}"' if value else f'{field_name}:["" TO *]')
            if selected
            else None
        )

    @classmethod
    def value_conditions(cls, field_name, field):
        return (
            cls.value_condition(field_name, key, value)
            for key, value in field.get("c", {}).items()
            if cls.value_condition(field_name, key, value) is not None
        )

    @classmethod
    def field_condition(cls, field_name, field):
        conditions = list(cls.value_conditions(field_name, field))
        return " OR ".join(f"({item})" for item in conditions) if conditions else ""

    def field_conditions(self):
        return (
            self.field_condition(name, value)
            for name, value in self.config.items()
            if self.field_condition(name, value)
        )

    @property
    def solr(self):
        conditions = list(self.field_conditions())
        if not conditions:
            return ""

        if len(conditions) == 1:
            return conditions[0]

        return " AND ".join(f"({condition})" for condition in conditions)

    @property
    def contains_query(self):
        return {
            f"f.{name}.facet.contains": config.get("p", "")
            for name, config in self.config.items()
            if config.get("p", "")
        }

    def more_query(self, facet_fields, multiplier):
        return {
            f"f.{field['name']}.facet.limit": (
                multiplier * self.limit_more
                if self.config.get(field["name"], {}).get("m", False)
                else multiplier * (self.limit_less + 1)
            )
            for field in facet_fields
        }

    def more_dict(self, facet_fields, multiplier):
        return {
            field["name"]: (
                multiplier * self.limit_more
                if self.config.get(field["name"], {}).get("m", False)
                else multiplier * (self.limit_less + 1)
            )
            for field in facet_fields
        }


def fix_value(v):
    # XXX this should probably fix in the catalog
    return None if v == "None" else v


def get_facet_fields_result(raw_facet_fields_result, facet_fields, more_dict):
    result = []

    for field_def in facet_fields:
        name = field_def["name"]
        full_array = raw_facet_fields_result[name]
        limit = more_dict[name]

        # Pair values with counts, fixing the value
        paired = zip(
            map(fix_value, full_array[::2]),
            full_array[1::2],
            strict=False,
        )

        # Filter out nulls, empty strings, and reverse tokens
        filtered = [
            (value, count)
            for value, count in paired
            if count > 0 and value and not value.startswith("\x01")
        ]

        # Slice to the desired limit
        result.append((field_def, filtered[:limit]))

    return result
