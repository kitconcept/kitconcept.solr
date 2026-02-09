from kitconcept.solr.services.solr_utils import escape
from kitconcept.solr.services.solr_utils import replace_reserved
from zExceptions import BadRequest

import base64
import binascii
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
            except (
                UnicodeDecodeError,
                json.decoder.JSONDecodeError,
                binascii.Error,
            ):
                logger.warning("Ignoring invalid base64 encoded string", exc_info=True)
                config = []
        else:
            config = []
        return cls(config)

    def query_list(self):
        results = []
        for row in self.config:
            try:
                [fieldname, kind, condition] = row
            except (TypeError, ValueError) as err:
                raise BadRequest(
                    f"Invalid extra condition row [{row}], needs: [fieldname, kind, condition]"  # noqa: E501
                ) from err
            fieldname = escape_fieldname(fieldname)
            if kind == "date-range":
                keys = set(condition.keys())
                if (
                    not keys.issubset({"ge", "le", "gr", "ls"})
                    or {"ge", "gr"}.issubset(keys)
                    or {"le", "ls"}.issubset(keys)
                ):
                    raise BadRequest(
                        f"invalid keys in options for condition 'date-range' [{keys}]"
                    )
                result = f"{fieldname}:"
                if "ge" in condition:
                    value = replace_reserved(condition["ge"])
                    result += f"[{value} TO "
                elif "gr" in condition:
                    value = replace_reserved(condition["gr"])
                    result += f"{{{value} TO "
                else:
                    result += "[* TO "
                if "le" in condition:
                    value = replace_reserved(condition["le"])
                    result += f"{value}]"
                elif "ls" in condition:
                    value = replace_reserved(condition["ls"])
                    result += f"{value}}}"
                else:
                    result += "*]"
            elif kind == "string":
                keys = set(condition.keys())
                if not keys.issubset({"in"}):
                    raise BadRequest(
                        "invalid keys in options for condition 'string', "
                        f"supported: 'in' [{keys}]"
                    )
                if "in" in condition:
                    if type(condition["in"]) is not list:
                        raise BadRequest(
                            "invalid type for condition 'string' "
                            f"[{type(condition['in'])}]"
                        )
                    if len(condition["in"]) == 0:
                        # Empty list, ignore
                        continue
                    result = f"{fieldname}:"
                    result += (
                        "("
                        + " OR ".join([
                            replace_reserved(term) for term in condition["in"]
                        ])
                        + ")"
                    )
            else:
                raise BadRequest(f"Wrong condition type [{kind}]")
            results.append(result)
        return results
