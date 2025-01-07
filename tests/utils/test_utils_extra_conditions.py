from kitconcept.solr.services.solr_utils_extra import SolrExtraConditions

import base64
import json
import pytest


def encoded(o):
    return base64.b64encode(json.dumps(o).encode("utf-8")).decode("ascii")


class TestUtilsExtraConditionsSolr:
    def test_from_encoded_valid(self):
        raw = encoded(
            [["start", "date-range", {"ge": "2021-02-01T00:00:00Z"}]]
        )
        obj = SolrExtraConditions.from_encoded(raw)
        assert obj.config == [
            ["start", "date-range", {"ge": "2021-02-01T00:00:00Z"}]
        ]

    def test_from_encoded_invalid_base64(self):
        raw = "abcdabcd"  # multiple of 4
        obj = SolrExtraConditions.from_encoded(raw)
        assert obj.config == []

    def test_from_encoded_invalid_base64_2(self):
        raw = "invalid_base64"
        obj = SolrExtraConditions.from_encoded(raw)
        assert obj.config == []

    def test_create_ignores_error_unicode(self):
        c = SolrExtraConditions.from_encoded(
            base64.b64encode('{"foo": "Atommüll"}'.encode("latin1")).decode(
                "ascii"
            )
        )
        assert c.config == []

    def test_create_ignores_error_json(self):
        c = SolrExtraConditions.from_encoded(
            base64.b64encode(b'{"foo": what is this, surely not json?').decode(
                "ascii"
            )
        )
        assert c.config == []

    def test_from_encoded_none(self):
        obj = SolrExtraConditions.from_encoded(None)
        assert obj.config == []

    def test_query_list_ge(self):
        config = [["start", "date-range", {"ge": "2021-02-01T00:00:00Z"}]]
        obj = SolrExtraConditions(config)
        result = obj.query_list()
        assert result == ["start:[2021-02-01T00:00:00Z TO *]"]

    def test_query_list_le(self):
        config = [["start", "date-range", {"le": "2021-02-01T00:00:00Z"}]]
        obj = SolrExtraConditions(config)
        result = obj.query_list()
        assert result == ["start:[* TO 2021-02-01T00:00:00Z]"]

    def test_query_list_gr(self):
        config = [["start", "date-range", {"gr": "2021-02-01T00:00:00Z"}]]
        obj = SolrExtraConditions(config)
        result = obj.query_list()
        assert result == ["start:{2021-02-01T00:00:00Z TO *]"]

    def test_query_list_ls(self):
        config = [["start", "date-range", {"ls": "2021-02-01T00:00:00Z"}]]
        obj = SolrExtraConditions(config)
        result = obj.query_list()
        assert result == ["start:[* TO 2021-02-01T00:00:00Z}"]

    def test_query_list_ge_le(self):
        config = [
            [
                "start",
                "date-range",
                {"ge": "2021-02-01T00:00:00Z", "le": "2021-03-01T00:00:00Z"},
            ]
        ]
        obj = SolrExtraConditions(config)
        result = obj.query_list()
        assert result == [
            "start:[2021-02-01T00:00:00Z TO 2021-03-01T00:00:00Z]"
        ]

    def test_query_list_invalid_keys(self):
        config = [["start", "date-range", {"invalid": "2021-02-01T00:00:00Z"}]]
        obj = SolrExtraConditions(config)
        with pytest.raises(RuntimeError):
            obj.query_list()

    def test_query_list_invalid_condition_type(self):
        config = [["start", "invalid-type", {"ge": "2021-02-01T00:00:00Z"}]]
        obj = SolrExtraConditions(config)
        with pytest.raises(RuntimeError):
            obj.query_list()

    def test_query_list_invalid_combination_1(self):
        config = [
            [
                "start",
                "date-range",
                {"ge": "2021-02-01T00:00:00Z", "gr": "2021-02-01T00:00:00Z"},
            ]
        ]
        obj = SolrExtraConditions(config)
        with pytest.raises(RuntimeError):
            obj.query_list()

    def test_query_list_invalid_combination_2(self):
        config = [
            [
                "start",
                "date-range",
                {"le": "2021-02-01T00:00:00Z", "ls": "2021-02-01T00:00:00Z"},
            ]
        ]
        obj = SolrExtraConditions(config)
        with pytest.raises(RuntimeError):
            obj.query_list()
