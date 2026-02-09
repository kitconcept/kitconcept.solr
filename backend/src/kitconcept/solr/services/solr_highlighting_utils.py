class SolrHighlightingUtils:
    fields: list
    enabled: bool
    propByField: dict

    def __init__(self, solr_config):
        highlightingFields = solr_config.config.get("highlightingFields", [])
        self.fields = [field["field"] for field in highlightingFields]
        self.enabled = len(self.fields) > 0
        self.propByField = {
            field["field"]: field["prop"] for field in highlightingFields
        }

    def enhance_items(self, items: list, highlighting: dict):
        if self.enabled:
            for item in items:
                for field, value in highlighting.get(item["UID"], {}).items():
                    item[self.propByField[field]] = value
