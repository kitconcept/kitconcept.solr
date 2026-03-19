from kitconcept.solr.interfaces import IKitconceptSolrSettings
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def add_highlighting_config(context):
    value = api.portal.get_registry_record("kitconcept.solr.config")
    if "highlightingFields" not in value:
        value["highlightingFields"] = [
            {"field": "content", "prop": "highlighting"},
            {"field": "Title", "prop": "highlighting_title"},
            {"field": "Description", "prop": "highlighting_description"},
        ]
        api.portal.set_registry_record("kitconcept.solr.config", value)


def update_registry_schema(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IKitconceptSolrSettings, prefix="kitconcept.solr")
