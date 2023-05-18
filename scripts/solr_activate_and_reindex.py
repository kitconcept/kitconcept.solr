from collective.solr.interfaces import ISolrConnectionManager
from plone.registry.interfaces import IRegistry
from Testing.makerequest import makerequest
from zope.component import getUtility
from zope.component import queryUtility
from zope.site.hooks import setSite

import logging
import sys
import transaction


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
        sys.exit(1)


def activate(active=True):
    """(de)activate the solr integration"""
    registry = getUtility(IRegistry)
    registry["collective.solr.active"] = active


def silence_logger():
    orig_logger_exception = indexer_logger.exception

    def new_logger_exception(msg):
        if msg != "Error occured while getting data for indexing!":
            orig_logger_exception(msg)

    indexer_logger.exception = new_logger_exception

    def reactivate_logger():
        indexer_logger.exception = orig_logger_exception

    return reactivate_logger


def reindex(portal):
    """reindex the existing content in solr"""
    maintenance = portal.unrestrictedTraverse("@@solr-maintenance")
    if "--clear" in sys.argv:
        logger.info("Clearing solr...")
        maintenance.clear()
    # Avoid throwing a lot of errors which are actually not errors,
    # but the indexer keeps throwing them when it tries to traverse everything.
    reactivate_logger = silence_logger()
    logger.info("Reindexing solr...")
    maintenance.reindex()
    reactivate_logger()


app = makerequest(app)  # noQA

# Set site to Plone
site_id = "Plone"
portal = app.unrestrictedTraverse(site_id)
setSite(portal)

# Activate before confirming solr is running,
# because the confirmation only works if solr is enabled in the registry.
# If solr isn't running, we'll exit
# before committing the transaction with the activation.
activate()
solr_must_be_running(portal)
reindex(portal)

transaction.commit()
app._p_jar.sync()
