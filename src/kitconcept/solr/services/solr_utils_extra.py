from .solr_utils import escape
from .solr_utils import replace_reserved

import base64
import json
import logging


logger = logging.getLogger("kitconcept.solr")
logger.setLevel(logging.DEBUG)


def escape_fieldname(fieldname):
    return replace_reserved(fieldname)


def escape_value(value):
    return '"' + (escape(value)) + '"'


class SolrExtraConditions:
    config: object

    def __init__(self, config: dict):
        self.config = config

    @classmethod
    def from_encoded(cls, raw: str):
        if raw is not None:
            try:
                config = json.loads(base64.b64decode(raw))
            except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                logger.warning(
                    "Ignoring invalid base64 encoded string", exc_info=True
                )
                config = {}
        else:
            config = {}
        return cls(config)

    def query_list(self):
        results = []
        for [fieldname, kind, condition] in self.config:
            fieldname = escape_fieldname(fieldname)
            if kind == "date-range":
                keys = set(condition.keys())
                if (
                    not keys.issubset({"ge", "le", "gr", "ls"})
                    or {"ge", "gr"}.issubset(keys)
                    or {"le", "ls"}.issubset(keys)
                ):
                    raise RuntimeError(
                        f"invalid keys in options for condition 'date-range' [{keys}]"
                    )
                result = f"{fieldname}:"
                if "ge" in condition:
                    value = replace_reserved(condition["ge"])
                    result += f"[{value} TO "
                elif "gr" in condition:
                    value = replace_reserved(condition["ge"])
                    result += f"{{{value} TO "
                else:
                    result += f"[* TO "
                if "le" in condition:
                    value = replace_reserved(condition["le"])
                    result += f"{value}]"
                elif "ls" in condition:
                    value = replace_reserved(condition["ls"])
                    result += f"{value}}}"
                else:
                    result += f"*]"
            else:
                raise RuntimeError(f"Wrong condition type [{kind}]")
            results.append(result)
        return results
