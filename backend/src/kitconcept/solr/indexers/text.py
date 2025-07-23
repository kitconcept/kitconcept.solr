from plone.indexer import indexer
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockSearchableText
from typing import Any
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


def safe_dict_traverse(data: dict, path: str, default: Any) -> Any:
    """Safe traverse a dict based on a path.

    :param data: Dictionary containing the data.
    :param path: Path to the value. i.e. about/value/0/children/text
    :param default: Default value, case the traverse fails.
    :returns: Value extracted from data.
    """
    error = False
    path = path[1:] if path.startswith("/") else path
    parts = path.split("/")
    value = default
    tmp_data = data
    for idx in parts:
        try:
            if isinstance(tmp_data, dict):
                tmp_data = tmp_data[idx]
            elif isinstance(tmp_data, list):
                tmp_data = tmp_data[int(idx)]
        except (KeyError, IndexError, ValueError):
            # Either the key does not exist in the dictionary
            # Or the index does not exist in the list
            # Or we have a list and the index is not a number
            error = True
            break
    if not error:
        value = tmp_data
    return value


def _extract_block_text(block: dict) -> str:
    """Extract text from a block.

    :param block: Dictionary with block information.
    :returns: A string with text found in the block.
    """
    block_type = block.get("@type", "")
    result = ""
    match block_type:
        case "headline":
            result = block.get("title", "")
        case "introduction":
            about = safe_dict_traverse(block, "about/value/0/children/0/text", "")
            topics = safe_dict_traverse(block, "topics/value/0/children/0/text", "")
            result = f"{about}\n{topics}"
        case "slateTable":
            for row in range(len(block["table"]["rows"])):
                for column in range(len(block["table"]["rows"][row])):
                    path = f"table/rows/{row}/cells/{column}/value/0/children/0/text"
                    cell = safe_dict_traverse(block, path, "")
                    result = f"{result}\n{cell}"
        case "tabBlock":
            tab = ""
            tab_amount = len(block["columns"])
            for i in range(tab_amount):
                path = f"text-{i}/blocks/0/text"
                tab = safe_dict_traverse(block, path, "")
                result = f"{result}\n{tab}"
    return result


def extract_text(block, obj, request):
    """Extract text information from a block.
    This function tries the following methods, until it finds a result:
        1. searchableText attribute
        2. Server side adapter
        3. Subblocks
    The decision to use the server side adapter before the subblocks traversal
    allows addon developers to choose this implementation when they want a
    more granular control of the indexing.
    :param block: Dictionary with block information.
    :param obj: Context to be used to get a IBlockSearchableText.
    :param request: Current request.
    :returns: A string with text found in the block.
    """
    result = ""
    block_type = block.get("@type", "")
    # searchableText is the conventional way of storing
    # searchable info in a block
    if searchableText := block.get("searchableText", ""):
        # TODO: should we evaluate in some way this value? maybe passing
        # it into html/plain text transformer?
        return searchableText
    elif plaintext := block.get("plaintext", ""):
        return plaintext
    elif text := block.get("text", ""):
        # Some blocks have the text attribute directly available (no richtext)
        return text

    if result := _extract_block_text(block):
        return result

    # Use server side adapters to extract the text data
    adapter = queryMultiAdapter((obj, request), IBlockSearchableText, name=block_type)
    result = adapter(block) if adapter is not None else ""
    if not result:
        subblocks = extract_subblocks(block)
        for subblock in subblocks:
            tmp_result = extract_text(subblock, obj, request)
            result = f"{result}\n{tmp_result}"
    return result


def extract_subblocks(block):
    """Extract subblocks from a block.
    :param block: Dictionary with block information.
    :returns: A list with subblocks, if present, or an empty list.
    """
    if "data" in block and "blocks" in block["data"]:
        raw_blocks = block["data"]["blocks"]
    elif "blocks" in block:
        raw_blocks = block["blocks"]
    else:
        raw_blocks = None
    if "columns" in block:
        # Check for grid block
        if block["@type"] == "__grid":
            columns = block["columns"]
            return columns
        return []
    return list(raw_blocks.values()) if isinstance(raw_blocks, dict) else []


@indexer(IBlocks)
def body_text_blocks(obj):
    """Index text to be used with Solr."""
    request = getRequest()
    blocks = obj.blocks
    blocks_layout = obj.blocks_layout
    blocks_text = []
    for block_id in blocks_layout.get("items", []):
        block = blocks.get(block_id, {})
        blocks_text.append(extract_text(block, obj, request))

    return " ".join([text.strip() for text in blocks_text if text.strip()])
