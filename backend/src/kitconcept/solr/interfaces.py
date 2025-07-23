"""Module where all interfaces, events and exceptions live."""

from kitconcept.solr import _
from plone.schema import JSONField
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import json


class IKitconceptSolrLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


CONFIG_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "fieldList": {
            "type": "array",
            "items": {"type": "string"},
        },
        "searchTabs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "filter": {"type": "string"},
                },
            },
        },
    },
})

DEFAULT_CONFIG = {
    "fieldList": [
        "UID",
        "Title",
        "Description",
        "Type",
        "effective",
        "start",
        "created",
        "end",
        "path_string",
        "mime_type",
        "phone",
        "email",
        "location",
        "image_scales",
        "image_field",
    ],
    "searchTabs": [
        {"label": "All", "filter": "Type(*)"},
        {"label": "Pages", "filter": "Type:(Page)"},
        {"label": "Events", "filter": "Type:(Event)"},
        {"label": "Images", "filter": "Type:(Image)"},
        {"label": "Files", "filter": "Type:(File)"},
    ],
}


class IKitconceptSolrSettings(Interface):
    config = JSONField(
        title=_("label_solr_config", default="Solr Config"),
        description=_("help_solr_config", default="Solr endpoint configuration"),
        required=True,
        schema=CONFIG_SCHEMA,
        default=DEFAULT_CONFIG,
        missing_value={"fieldList": [], "searchTabs": []},
    )
