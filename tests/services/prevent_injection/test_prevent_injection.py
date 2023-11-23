import pytest


class TestPreventInjection:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestInjectionOfUppercaseOperatorsIsAvoided(TestPreventInjection):
    url = "/@solr?q=red%20NOT%20blue"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # We test that the NOT word is interpreted as a word and not as a logical
            # operator.
            # If it were, then only document2 would be found which would mean an injection
            # is possible.
            ("/plone/document1", True),
            ("/plone/document2", True),
            ("/plone/AnD_oR_nOt_WHATnot", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestMixedCaseOperatorsAreNotLowercased(TestPreventInjection):
    url = "/@solr?q=AnD_oR_nOt_WHATnot"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Id is string type and case sensitive so we can test that case sensitivity
            # is not stripped from the service.
            ("/plone/AnD_oR_nOt_WHATnot", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestMixedCaseOperatorsAreNotLowercasedStandalone(TestPreventInjection):
    url = "/@solr?q=oR"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Id is string type and case sensitive so we can test that case sensitivity
            # is not stripped from the service.
            ("/plone/oR", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestMixedCaseOperatorsAreNotLowercasedIfContainedOnly(TestPreventInjection):
    url = "/@solr?q=ANDoR"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Id is string type and case sensitive so we can test that case sensitivity
            # is not stripped from the service.
            ("/plone/ANDoR", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestMixedCaseOperatorsAreNotLowercasedIfContainedOnly2(TestPreventInjection):
    url = "/@solr?q=ANdOR"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Id is string type and case sensitive so we can test that case sensitivity
            # is not stripped from the service.
            ("/plone/ANdOR", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestMixedCaseOperatorsAreNotLowercasedIfContainedOnly3(TestPreventInjection):
    url = "/@solr?q=OReo"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Id is string type and case sensitive so we can test that case sensitivity
            # is not stripped from the service.
            ("/plone/OReo", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestInjectionOfSymbolOperatorsIsAvoided(TestPreventInjection):
    url = "/@solr?q=red%20!%20blue"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # We test that the ! operator is interpreted as a word and not as a logical
            # operator.
            # If it were, then only document2 would be found which would mean an injection
            # is possible.
            ("/plone/document1", True),
            ("/plone/document2", True),
            ("/plone/AnD_oR_nOt_WHATnot", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected


class TestInjectionOfUrlComponentsIsAvoided(TestPreventInjection):
    url = "/@solr?q=red%20%26%20blue"

    @pytest.mark.parametrize(
        "path,expected",
        [
            # We test that the encoded form of & cannot in some way turn into a & in the
            # solr query
            # which would allow feeding arbitrary parameters other than q into the
            # solr server.
            ("/plone/document1", True),
            ("/plone/document2", True),
            ("/plone/AnD_oR_nOt_WHATnot", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected
