from kitconcept.solr.reindex_helpers import activate_and_reindex
from Testing.makerequest import makerequest
from zope.site.hooks import setSite

import sys
import transaction


if __name__ == "__main__":
    app = makerequest(globals()["app"])

    # Set site to Plone
    site_id = "Plone"
    portal = app.unrestrictedTraverse(site_id)
    setSite(portal)

    # --rag-enable / --rag-disable switch the AI search registry toggle
    # (before reindexing, so enabling also builds the RAG chunks);
    # without either flag the toggle is left unchanged.
    rag = None
    if "--rag-enable" in sys.argv:
        rag = True
    elif "--rag-disable" in sys.argv:
        rag = False

    activate_and_reindex(portal, clear="--clear" in sys.argv, rag=rag)

    transaction.commit()
    app._p_jar.sync()
