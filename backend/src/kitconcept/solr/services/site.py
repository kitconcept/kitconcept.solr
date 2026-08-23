from collective.solr.utils import isActive
from kitconcept.solr.interfaces import IKitconceptSolrLayer
from kitconcept.solr.rag.config import get_rag_config
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


try:
    from plone.restapi.interfaces import ISiteEndpointExpander
except ImportError:
    # added in plone.restapi 9.14.0
    class ISiteEndpointExpander(Interface):
        pass


@adapter(Interface, IKitconceptSolrLayer)
@implementer(ISiteEndpointExpander)
class CollectiveSolrExpander:
    """Add solr/RAG availability to the @site endpoint.

    The @site endpoint is loaded by Volto on every SSR page load into
    the redux store, so the client knows these values before the first
    render.

    kitconcept.solr.rag_available carries the EFFECTIVE state of the
    AI search: the registry toggle is on AND the LLM endpoint
    credentials are configured. Decision: graceful degradation - a
    toggle without credentials (or a downed AI service) silently falls
    back to the classic search instead of raising a hard error (see
    SPECIFICATION-79.md, decisions record).
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, data):
        data["collective.solr.active"] = isActive()
        data["kitconcept.solr.rag_available"] = get_rag_config() is not None
