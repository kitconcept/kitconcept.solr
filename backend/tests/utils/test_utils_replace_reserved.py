from kitconcept.solr.services.solr_utils import replace_reserved


class TestUtilsReplaceReserved:
    def test_replace_reserved_and(self):
        assert replace_reserved("foo AND bar") == "foo and bar"

    def test_replace_reserved_or(self):
        assert replace_reserved("foo OR bar") == "foo or bar"

    def test_replace_reserved_not(self):
        assert replace_reserved("foo NOT bar") == "foo not bar"

    def test_replace_reserved_keep_lowercase(self):
        assert replace_reserved("foo AnD NoT bar Or OReo") == "foo AnD NoT bar Or OReo"

    def test_replace_reserved_keep_partial_match(self):
        assert replace_reserved("OReo ANDroid kNOT") == "OReo ANDroid kNOT"
