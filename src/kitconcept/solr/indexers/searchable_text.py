from plone.app.contenttypes.indexers import SearchableText_file
from plone.app.contenttypes.interfaces import IImage
from plone.indexer import indexer


@indexer(IImage)
def searchable_text_image(obj):
    """Implement SearchableText for Image content."""
    return SearchableText_file(obj)
