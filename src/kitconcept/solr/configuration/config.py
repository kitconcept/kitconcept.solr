from pathlib import Path
from zope.component import getUtility
from .interface import ISolrConfig

import json
import os
import os.path


def get_solr_config():
    handler = getUtility(ISolrConfig)
    return handler()


solr_config = None


def provide_solr_config():
    global solr_config
    if solr_config is not None:
        # Only read the file once
        return solr_config
    solr_config_path = os.path.join(Path(__file__).parent.resolve(), "solr-config.json")
    try:
        with open(solr_config_path) as solr_config_file:
            solr_config = json.load(solr_config_file)
    except Exception:  # noqa
        raise RuntimeError(f"Error loading json config from {solr_config_path}")
    return solr_config
