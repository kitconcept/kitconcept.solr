from pathlib import Path

import json
import os
import os.path

SOLR_CONTEXT_FOLDER = os.environ.get("SOLR_CONTEXT_FOLDER")
if not SOLR_CONTEXT_FOLDER:
    # Use the default from the current package
    current = Path(__file__).parent.resolve()
    SOLR_CONTEXT_FOLDER = os.path.join(current, "..", "..", "..", "..", "solr")
    # / or:
    # raise RuntimeError("SOLR_CONTEXT_FOLDER must be defined")

solr_config_path = os.path.join(SOLR_CONTEXT_FOLDER, "etc", "solr-config.json")

try:
    with open(solr_config_path) as solr_config_file:
        solr_config = json.load(solr_config_file)
except Exception:  # noqa
    raise RuntimeError(f"Error loading json config from {solr_config_path}")


filters = None
field_list = None


def get_filters():
    global filters
    if filters is None:
        try:
            filters = list(map(lambda item: item["filter"], solr_config["searchTabs"]))
        except Exception:  # noqa
            raise RuntimeError(
                f"Error parsing json config from {solr_config_path} {solr_config}"
            )
    return filters


def solr_select_condition(group_select):
    return "{!tag=typefilter}" + get_filters()[group_select]


def solr_facet_query():
    return list(map(lambda item: "{!ex=typefilter}" + item, get_filters()))


class SolrConfigError(RuntimeError):
    pass


def solr_field_list():
    global field_list

    def check_item(item):
        if "," in item:
            raise SolrConfigError(
                f"Error parsing json config from {solr_config_path} {solr_config}, fieldList item contains comma (,) which is prohibited"
            )
        return item

    if field_list is None:
        try:
            field_list = ",".join(map(check_item, solr_config["fieldList"]))
        except Exception as err:  # noqa
            if isinstance(err, SolrConfigError):
                raise
            else:
                raise SolrConfigError(
                    f"Error parsing json config from {solr_config_path} {solr_config}"
                )
    return field_list

    return
