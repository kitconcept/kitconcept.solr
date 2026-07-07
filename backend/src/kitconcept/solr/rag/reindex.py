"""Full reindex of the RAG chunk documents.

collective.solr's ``@@solr-maintenance`` reindex walks the content
objects and talks to Solr directly, bypassing the indexing queue
processors — so a full reindex would never (re)build the RAG chunks.
This module provides the equivalent pass for the chunks; it is called
from ``reindex_helpers.reindex`` after the regular Solr reindex.
"""

from collective.solr.interfaces import ICheckIndexable
from collective.solr.interfaces import ISolrConnectionManager
from collective.solr.utils import findObjects
from kitconcept.solr.rag.config import get_rag_config
from kitconcept.solr.rag.processor import RagIndexProcessor
from zope.component import queryUtility

import logging


logger = logging.getLogger("kitconcept.solr.rag")

COMMIT_BATCH = 100


def reindex_rag(portal) -> int:
    """Rebuild the RAG chunk documents for all indexable content.

    Returns the number of processed objects. A no-op (returning 0)
    when the RAG feature is not enabled and configured.
    """
    config = get_rag_config()
    if config is None:
        logger.info("RAG is not enabled/configured, skipping chunk reindex.")
        return 0
    manager = queryUtility(ISolrConnectionManager, context=portal)
    conn = manager.getConnection() if manager is not None else None
    if conn is None:
        logger.warning("No Solr connection, skipping chunk reindex.")
        return 0
    processor = RagIndexProcessor(manager)
    logger.info("Reindexing RAG chunks...")
    processed = 0
    for _path, obj in findObjects(portal):
        if not ICheckIndexable(obj)():
            continue
        processor.index(obj)
        processed += 1
        if processed % COMMIT_BATCH == 0:
            conn.commit(soft=True)
            logger.info("intermediate commit (%d items processed)", processed)
    conn.commit(soft=True)
    logger.info("RAG chunk reindex done, %d items processed.", processed)
    return processed
