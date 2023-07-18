from ..configuration.config import get_solr_config


filters = None
field_list = None
labels = None


def get_filters(solr_config):
    global filters
    if filters is None:
        try:
            filters = list(map(lambda item: item["filter"], solr_config["searchTabs"]))
        except Exception:  # noqa
            raise RuntimeError(f"Error parsing solr config {solr_config}")
    return filters


def get_labels(solr_config):
    global labels
    if labels is None:
        try:
            labels = list(map(lambda item: item["label"], solr_config["searchTabs"]))
        except Exception:  # noqa
            raise RuntimeError(f"Error parsing solr config {solr_config}")
    return labels


def solr_select_condition(group_select):
    solr_config = get_solr_config()
    return "{!tag=typefilter}" + get_filters(solr_config)[group_select]


def solr_facet_query():
    solr_config = get_solr_config()
    return list(map(lambda item: "{!ex=typefilter}" + item, get_filters(solr_config)))


class SolrConfigError(RuntimeError):
    pass


def solr_field_list():
    global field_list
    solr_config = get_solr_config()

    def check_item(item):
        if "," in item:
            raise SolrConfigError(
                f"Error parsing solr config {solr_config}, fieldList item contains comma (,) which is prohibited"
            )
        return item

    if field_list is None:
        try:
            field_list = ",".join(map(check_item, solr_config["fieldList"]))
        except Exception as err:  # noqa
            if isinstance(err, SolrConfigError):
                raise
            else:
                raise SolrConfigError(f"Error parsing solr config {solr_config}")
    return field_list


def solr_labels():
    solr_config = get_solr_config()
    return get_labels(solr_config)
