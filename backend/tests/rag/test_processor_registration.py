from kitconcept.solr.rag.processor import RagIndexProcessor
from Products.CMFCore.interfaces import IIndexQueueProcessor
from zope.component import getUtilitiesFor


class TestQueueProcessorRegistration:
    def test_utility_registered_on_install(self, portal):
        utilities = dict(getUtilitiesFor(IIndexQueueProcessor))
        assert "kitconcept.solr.rag" in utilities
        assert isinstance(utilities["kitconcept.solr.rag"], RagIndexProcessor)

    def test_collective_solr_processor_still_registered(self, portal):
        utilities = dict(getUtilitiesFor(IIndexQueueProcessor))
        assert "solr" in utilities
