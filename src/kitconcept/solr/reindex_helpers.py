from collective.solr.interfaces import ISolrConnectionManager
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


def activate_and_reindex(portal, clear=False):
    # Activate before confirming solr is running,
    # because the confirmation only works if solr is enabled in the registry.
    # If solr isn't running, we'll exit
    # before committing the transaction with the activation.
    activate()
    if solr_must_be_running(portal):
        reindex(portal, clear=clear)
