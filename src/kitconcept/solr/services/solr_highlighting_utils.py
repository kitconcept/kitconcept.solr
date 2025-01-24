class SolrHighlightingUtils:
    fields: list
    enabled: bool
    propByField: dict

    def __init__(self, solr_config):
        highlightingFields = solr_config.config.get("highlightingFields", [])
        self.fields = list(
            map(lambda field: field["field"], highlightingFields)
        )
        self.enabled = len(self.fields) > 0
        self.propByField = dict(
            map(
                lambda field: (field["field"], field["prop"]),
                highlightingFields,
            )
        )

    def enhance_items(self, items: list, highlighting: dict):
        if self.enabled:
            for item in items:
                for field, value in highlighting.get(item["UID"], {}).items():
                    print("Enhance item", item, field, value)
                    item[self.propByField[field]] = value
