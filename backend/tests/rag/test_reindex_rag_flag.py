from kitconcept.solr import reindex_helpers
from kitconcept.solr.rag.config import REGISTRY_ENABLED_KEY
from plone import api
from unittest import mock

import pytest


@pytest.fixture
def quiet_reindex():
    """Skip the actual solr reindex parts."""
    with (
        mock.patch.object(reindex_helpers, "solr_must_be_running", return_value=False),
        mock.patch.object(reindex_helpers, "activate"),
    ):
        yield


class TestActivateAndReindexRagFlag:
    def test_default_leaves_toggle_unchanged(self, portal, quiet_reindex):
        assert api.portal.get_registry_record(REGISTRY_ENABLED_KEY) is False
        reindex_helpers.activate_and_reindex(portal)
        assert api.portal.get_registry_record(REGISTRY_ENABLED_KEY) is False

    def test_rag_true_enables_toggle(self, portal, quiet_reindex):
        try:
            reindex_helpers.activate_and_reindex(portal, rag=True)
            assert api.portal.get_registry_record(REGISTRY_ENABLED_KEY) is True
        finally:
            api.portal.set_registry_record(REGISTRY_ENABLED_KEY, False)

    def test_rag_false_disables_toggle(self, portal, quiet_reindex):
        api.portal.set_registry_record(REGISTRY_ENABLED_KEY, True)
        reindex_helpers.activate_and_reindex(portal, rag=False)
        assert api.portal.get_registry_record(REGISTRY_ENABLED_KEY) is False
