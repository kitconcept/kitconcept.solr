from kitconcept.solr.services.solr_utils import FacetConditions
from kitconcept.solr.services.solr_utils import get_facet_fields_result

import base64
import json
import pytest


def encoded(o):
    return base64.b64encode(json.dumps(o).encode("utf-8")).decode("ascii")


class TestUtilsFacetConditionsSolr:
    def test_create(self):
        o = {
            "field1": {"c": {"foo": True, "bar": True}},
            "field2": {"c": {"baz": True, "bae": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.config == o

    def test_create_none(self):
        c = FacetConditions.from_encoded(None)
        assert c.config == {}

    def test_create_ignores_error_unicode(self):
        c = FacetConditions.from_encoded(
            base64.b64encode('{"foo": "Atommüll"}'.encode("latin1")).decode("ascii")
        )
        assert c.config == {}

    def test_create_ignores_error_json(self):
        c = FacetConditions.from_encoded(
            base64.b64encode(b'{"foo": what is this, surely not json?').decode("ascii")
        )
        assert c.config == {}

    @pytest.mark.parametrize(
        "name,value,expected",
        [
            (
                "solr",
                {
                    "field1": {"c": {"foo": True, "bar": True}},
                    "field2": {"c": {"baz": True, "bae": True}},
                },
                '((field1:"foo") OR (field1:"bar")) AND ((field2:"baz") OR (field2:"bae"))',
            ),
            ("empty", {}, ""),
            (
                "ignores_false",
                {
                    "field1": {"c": {"foo": True, "bar": True}},
                    "field2": {"c": {"baz": True, "bae": True, "bax": False}},
                },
                '((field1:"foo") OR (field1:"bar")) AND ((field2:"baz") OR (field2:"bae"))',
            ),
            (
                "collapses_parent_or",
                {
                    "field1": {"c": {"foo": True, "bar": True}},
                    "field2": {"c": {"baz": True}},
                },
                '((field1:"foo") OR (field1:"bar")) AND ((field2:"baz"))',
            ),
            (
                "collapses_parent_or_with_false",
                {
                    "field1": {"c": {"foo": True, "bar": True}},
                    "field2": {"c": {"baz": True, "bae": False}},
                },
                '((field1:"foo") OR (field1:"bar")) AND ((field2:"baz"))',
            ),
            (
                "collapses_parent_and",
                {
                    "field1": {"c": {"foo": True, "bar": True}},
                },
                '(field1:"foo") OR (field1:"bar")',
            ),
            (
                "collapses_parent_and_with_false",
                {
                    "field1": {"c": {"foo": True, "bar": True}},
                    "field2": {"c": {"baz": False}},
                },
                '(field1:"foo") OR (field1:"bar")',
            ),
            (
                "collapses_parent_and_case2",
                {"field1": {"c": {"foo": True, "bar": True}}, "field2": {"c": {}}},
                '(field1:"foo") OR (field1:"bar")',
            ),
            (
                "collapses_parent_and_case3",
                {"field1": {"c": {"foo": True, "bar": True}}, "field2": {}},
                '(field1:"foo") OR (field1:"bar")',
            ),
            (
                "empty_value",
                {
                    "field1": {"c": {"foo": True, "": True}},
                    "field2": {"c": {"baz": True, "": True}},
                },
                '((field1:"foo") OR (field1:["" TO *])) AND ((field2:"baz") OR (field2:["" TO *]))',
            ),
        ],
    )
    def test_solr(self, name: str, value: dict, expected: str):
        c = FacetConditions.from_encoded(encoded(value))
        assert c.solr == expected, f"{name}: Expected {expected} but got {c.solr}"


class TestUtilsFacetConditionsPrefixQuery:
    def test_create(self):
        o = {
            "field1": {"p": "pre1"},
            "field2": {"p": "pre2"},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.config == o

    def test_create_none(self):
        c = FacetConditions.from_encoded(None)
        assert c.config == {}

    def test_prefix(self):
        o = {
            "field1": {"p": "pre1"},
            "field2": {"p": "pre2"},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.contains_query == {
            "f.field1.facet.contains": "pre1",
            "f.field2.facet.contains": "pre2",
        }

    def test_empty_field(self):
        o = {
            "field1": {"p": "pre1"},
            "field2": {},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.contains_query == {"f.field1.facet.contains": "pre1"}

    def test_empty_field_case2(self):
        o = {
            "field1": {"p": "pre1"},
            "field2": {"c": {"baz": True, "": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.contains_query == {"f.field1.facet.contains": "pre1"}

    def test_all_empty(self):
        o = {
            "field2": {"c": {"baz": True, "": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.contains_query == {}


class TestUtilsFacetConditionsMoreQuery:
    def test_create(self):
        o = {
            "field1": {"m": True},
            "field2": {"m": False},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.config == o

    def test_create_none(self):
        c = FacetConditions.from_encoded(None)
        assert c.config == {}

    def test_more(self):
        o = {
            "field1": {"m": True},
            "field2": {"m": False},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_query(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "f.field1.facet.limit": 200,
            "f.field2.facet.limit": 12,
            "f.field3.facet.limit": 12,
        }

    def test_empty_field(self):
        o = {
            "field1": {"m": True},
            "field2": {},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_query(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "f.field1.facet.limit": 200,
            "f.field2.facet.limit": 12,
            "f.field3.facet.limit": 12,
        }

    def test_empty_field_case2(self):
        o = {
            "field1": {"m": True},
            "field2": {"c": {"baz": True, "": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_query(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "f.field1.facet.limit": 200,
            "f.field2.facet.limit": 12,
            "f.field3.facet.limit": 12,
        }

    def test_all_empty(self):
        o = {
            "field2": {"c": {"baz": True, "": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_query(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "f.field1.facet.limit": 12,
            "f.field2.facet.limit": 12,
            "f.field3.facet.limit": 12,
        }


class TestUtilsFacetConditionsMoreDict:
    def test_create(self):
        o = {
            "field1": {"m": True},
            "field2": {"m": False},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.config == o

    def test_create_none(self):
        c = FacetConditions.from_encoded(None)
        assert c.config == {}

    def test_more(self):
        o = {
            "field1": {"m": True},
            "field2": {"m": False},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_dict(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "field1": 200,
            "field2": 12,
            "field3": 12,
        }

    def test_empty_field(self):
        o = {
            "field1": {"m": True},
            "field2": {},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_dict(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "field1": 200,
            "field2": 12,
            "field3": 12,
        }

    def test_empty_field_case2(self):
        o = {
            "field1": {"m": True},
            "field2": {"c": {"baz": True, "": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_dict(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "field1": 200,
            "field2": 12,
            "field3": 12,
        }

    def test_all_empty(self):
        o = {
            "field2": {"c": {"baz": True, "": True}},
        }
        c = FacetConditions.from_encoded(encoded(o))
        assert c.more_dict(
            [{"name": "field1"}, {"name": "field2"}, {"name": "field3"}],
            multiplier=2,
        ) == {
            "field1": 12,
            "field2": 12,
            "field3": 12,
        }


class TestUtilsGetFacetFieldsResult:
    def test_field_results(self):
        raw_facet_fields_result = {
            "field1": ["foo", 3, "bar", 2],
            "field2": ["baz", 1],
            "field3": ["ignored", 1],
        }
        facet_fields = [
            {"name": "field1", "label": "x"},
            {"name": "field2", "label": "y"},
        ]
        more_dict = {"field1": 5, "field2": 5}
        assert get_facet_fields_result(
            raw_facet_fields_result, facet_fields, more_dict
        ) == [
            ({"name": "field1", "label": "x"}, [("foo", 3), ("bar", 2)]),
            ({"name": "field2", "label": "y"}, [("baz", 1)]),
        ]

    def test_field_results_ignores_zero_count(self):
        raw_facet_fields_result = {
            "field1": ["foo", 3, "bar", 2, "baz", 0],
            "field2": ["baz", 1],
            "field3": ["ignored", 1],
        }
        facet_fields = [
            {"name": "field1", "label": "x"},
            {"name": "field2", "label": "y"},
        ]
        more_dict = {"field1": 5, "field2": 5}
        assert get_facet_fields_result(
            raw_facet_fields_result, facet_fields, more_dict
        ) == [
            ({"name": "field1", "label": "x"}, [("foo", 3), ("bar", 2)]),
            ({"name": "field2", "label": "y"}, [("baz", 1)]),
        ]

    def test_field_results_ignores_empty_value(self):
        raw_facet_fields_result = {
            "field1": ["foo", 3, "bar", 2, "", 12],
            "field2": ["baz", 1],
            "field3": ["ignored", 1],
        }
        facet_fields = [
            {"name": "field1", "label": "x"},
            {"name": "field2", "label": "y"},
        ]
        more_dict = {"field1": 5, "field2": 5}
        assert get_facet_fields_result(
            raw_facet_fields_result, facet_fields, more_dict
        ) == [
            ({"name": "field1", "label": "x"}, [("foo", 3), ("bar", 2)]),
            ({"name": "field2", "label": "y"}, [("baz", 1)]),
        ]

    def test_field_results_ignores_none_value(self):
        raw_facet_fields_result = {
            "field1": ["foo", 3, "bar", 2, None, 12],
            "field2": ["baz", 1],
            "field3": ["ignored", 1],
        }
        facet_fields = [
            {"name": "field1", "label": "x"},
            {"name": "field2", "label": "y"},
        ]
        more_dict = {"field1": 5, "field2": 5}
        assert get_facet_fields_result(
            raw_facet_fields_result, facet_fields, more_dict
        ) == [
            ({"name": "field1", "label": "x"}, [("foo", 3), ("bar", 2)]),
            ({"name": "field2", "label": "y"}, [("baz", 1)]),
        ]

    def test_field_results_ignores_reverse_value(self):
        raw_facet_fields_result = {
            "field1": ["foo", 3, "bar", 2, "\x01rab", 12],
            "field2": ["baz", 1],
            "field3": ["ignored", 1],
        }
        facet_fields = [
            {"name": "field1", "label": "x"},
            {"name": "field2", "label": "y"},
        ]
        more_dict = {"field1": 5, "field2": 5}
        assert get_facet_fields_result(
            raw_facet_fields_result, facet_fields, more_dict
        ) == [
            ({"name": "field1", "label": "x"}, [("foo", 3), ("bar", 2)]),
            ({"name": "field2", "label": "y"}, [("baz", 1)]),
        ]

    def test_field_results_moredict_limits(self):
        raw_facet_fields_result = {
            "field1": [
                "foo",
                3,
                "\x01oof",
                3,
                "bar",
                2,
                "\x01rab",
                12,
                "bax",
                1,
            ],
            "field2": ["baz", 1, "baba", 1],
            "field3": ["ignored", 1],
        }
        facet_fields = [
            {"name": "field1", "label": "x"},
            {"name": "field2", "label": "y"},
        ]
        more_dict = {"field1": 3, "field2": 1}
        assert get_facet_fields_result(
            raw_facet_fields_result, facet_fields, more_dict
        ) == [
            (
                {"name": "field1", "label": "x"},
                [("foo", 3), ("bar", 2), ("bax", 1)],
            ),
            ({"name": "field2", "label": "y"}, [("baz", 1)]),
        ]
