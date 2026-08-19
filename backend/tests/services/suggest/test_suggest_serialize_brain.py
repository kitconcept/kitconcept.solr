"""Serialization of individual suggestions.

These tests do not need Solr: they exercise `serialize_brain()` directly, so
they only request the `integration` fixture and never the Solr-backed `portal`
fixture from the enclosing conftest.

`Document` stands in for the folderish suggest type here. With plone.volto
applied it is a Dexterity `Container`, so plone.restapi serializes it with
`SerializeFolderToJson` - exactly the situation that makes the child listing
leak into the suggest payload.
"""

from kitconcept.solr.services import suggest as suggest_module
from kitconcept.solr.services.suggest import SolrSuggest
from plone import api

import pytest


@pytest.fixture
def service(integration):
    service = SolrSuggest()
    service.context = integration["portal"]
    service.request = integration["request"]
    return service


@pytest.fixture
def folderish_brain(integration):
    """A brain for a folderish object that has a child."""
    portal = integration["portal"]
    with api.env.adopt_roles(["Manager"]):
        parent = api.content.create(
            container=portal, type="Document", id="a-parent", title="A Parent"
        )
        api.content.create(
            container=parent, type="Document", id="a-child", title="A Child"
        )
    return api.content.find(UID=parent.UID())[0]


@pytest.fixture
def serialize_document_in_full(monkeypatch):
    monkeypatch.setattr(suggest_module, "FULL_SERIALIZATION_TYPES", ("Document",))


class TestSerializeBrain:
    def test_summary_serialization_is_the_default(self, service, folderish_brain):
        data = service.serialize_brain(folderish_brain)

        # The summary serializer does not report folderishness at all, which is
        # how we know the full serializer was not used here.
        assert "is_folderish" not in data
        assert "items" not in data

    def test_full_serialization_omits_the_child_listing(
        self, service, folderish_brain, serialize_document_in_full
    ):
        data = service.serialize_brain(folderish_brain)

        # We really did go through SerializeFolderToJson ...
        assert data["is_folderish"] is True
        # ... but none of its expensive extras made it into the payload.
        assert "items" not in data
        assert "items_total" not in data
        assert "batching" not in data

    def test_full_serialization_omits_the_expansion_components(
        self, service, folderish_brain, serialize_document_in_full
    ):
        data = service.serialize_brain(folderish_brain)

        # `include_expansion=False`: no `@components` expansion links
        # (breadcrumbs, navigation, actions...) in the suggest payload.
        assert "@components" not in data

    def test_full_serialization_still_returns_the_object(
        self, service, folderish_brain, serialize_document_in_full
    ):
        data = service.serialize_brain(folderish_brain)

        assert data["@id"].endswith("/a-parent")
        assert data["@type"] == "Document"
        assert data["title"] == "A Parent"
