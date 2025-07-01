from collective.solr.utils import isActive
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from kitconcept.solr.interfaces import IKitconceptSolrLayer

try:
    from plone.restapi.interfaces import ISiteEndpointExpander
except ImportError:
    # added in plone.restapi 9.14.0
    class ISiteEndpointExpander(Interface):
        pass

@adapter(Interface, IKitconceptSolrLayer)
@implementer(ISiteEndpointExpander)
class CollectiveSolrExpander:
    """Add collective.solr.active to the @site endpoint"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, data):
        data["collective.solr.active"] = isActive()
