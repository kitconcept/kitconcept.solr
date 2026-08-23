from collective.solr.interfaces import ISolrConnectionManager
from kitconcept.solr.rag.reindex import reindex_rag
from plone import api
from zope.component import queryUtility

import logging


logger = logging.getLogger("kitconcept.solr")
logger.setLevel(logging.DEBUG)

indexer_logger = logging.getLogger("collective.solr.indexer")


def solr_is_running(portal):
    manager = queryUtility(ISolrConnectionManager, context=portal)
    schema = manager.getSchema()
    return schema is not None


def solr_must_be_running(portal):
    if not solr_is_running(portal):
        logger.fatal("*** Solr must be running! (make solr-start) ***")
        return False
    return True


def activate(active=True):
    """(de)activate the solr integration"""
    api.portal.set_registry_record("collective.solr.active", active)


def set_rag_enabled(enabled):
    """Switch the RAG (AI search) registry toggle on or off.

    A runtime switch (no restart needed) - the effective availability
    additionally requires the LLM endpoint env vars, see
    kitconcept.solr.rag.config.get_rag_config.
    """
    api.portal.set_registry_record("kitconcept.solr.rag_enabled", enabled)


def silence_logger():
    orig_logger_exception = indexer_logger.exception

    def new_logger_exception(msg):
        if msg != "Error occured while getting data for indexing!":
            orig_logger_exception(msg)

    indexer_logger.exception = new_logger_exception

    def reactivate_logger():
        indexer_logger.exception = orig_logger_exception

    return reactivate_logger


def reindex(portal, clear=False):
    """reindex the existing content in solr"""
    maintenance = portal.unrestrictedTraverse("@@solr-maintenance")
    if clear:
        logger.info("Clearing solr...")
        maintenance.clear()
    # Avoid throwing a lot of errors which are actually not errors,
    # but the indexer keeps throwing them when it tries to traverse everything.
    reactivate_logger = silence_logger()
    logger.info("Reindexing solr...")
    maintenance.reindex()
    reactivate_logger()
    # The maintenance view above talks to Solr directly, bypassing the
    # indexing queue processors - the RAG chunks need their own pass.
    # (No-op unless the RAG feature is enabled and configured.)
    reindex_rag(portal)


def activate_and_reindex(portal, clear=False, rag=None):
    # Activate before confirming solr is running,
    # because the confirmation only works if solr is enabled in the registry.
    # If solr isn't running, we'll exit
    # before committing the transaction with the activation.
    activate()
    if rag is not None:
        # Set before reindexing, so that enabling also builds the RAG
        # chunks in the same pass. Note: disabling does not remove
        # already indexed chunks (they stay invisible and harmless);
        # a clear reindex removes them.
        set_rag_enabled(rag)
    if solr_must_be_running(portal):
        reindex(portal, clear=clear)
