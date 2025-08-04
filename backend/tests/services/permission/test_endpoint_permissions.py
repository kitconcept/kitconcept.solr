import pytest


@pytest.fixture()
def member_request(request_factory, user_credentials):
    request = request_factory()
    request.auth = user_credentials
    yield request
    request.auth = ()


class TestEndpointPerms:
    url = "/@solr?q=chomsky"

    @pytest.fixture
    def api_request(self, request_factory, users_credentials_role):
        def func(role: str) -> dict:
            req = request_factory()
            credentials = users_credentials_role.get(role, None)
            if credentials:
                req.auth = credentials
            return req

        return func

    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content):
        self.portal = portal_with_content


class TestEndpointPermsAll(TestEndpointPerms):
    @pytest.mark.parametrize(
        "role,path,expected",
        [
            ("anonymous", "/plone/noamchomsky", True),
            ("anonymous", "/plone/mynews", True),
            ("anonymous", "/plone/chomskysdocument", False),
            ("member", "/plone/noamchomsky", True),
            ("member", "/plone/mynews", True),
            ("member", "/plone/chomskysdocument", False),
            ("manager", "/plone/noamchomsky", True),
            ("manager", "/plone/mynews", True),
            ("manager", "/plone/chomskysdocument", True),
        ],
    )
    def test_paths(
        self,
        api_request,
        all_path_string,
        role: str,
        path: str,
        expected: bool,
    ):
        data = api_request(role).get(self.url).json()
        path_strings = all_path_string(data)
        assert (path in path_strings) is expected


class TestEndpointPermsGroup0(TestEndpointPerms):
    """group=All"""

    url = "/@solr?q=chomsky&group_select=0"

    @pytest.mark.parametrize(
        "role,path,expected",
        [
            ("anonymous", "/plone/noamchomsky", True),
            ("anonymous", "/plone/mynews", True),
            ("anonymous", "/plone/chomskysdocument", False),
            ("member", "/plone/noamchomsky", True),
            ("member", "/plone/mynews", True),
            ("member", "/plone/chomskysdocument", False),
            ("manager", "/plone/noamchomsky", True),
            ("manager", "/plone/mynews", True),
            ("manager", "/plone/chomskysdocument", True),
        ],
    )
    def test_paths(
        self,
        api_request,
        all_path_string,
        role: str,
        path: str,
        expected: bool,
    ):
        data = api_request(role).get(self.url).json()
        path_strings = all_path_string(data)
        assert (path in path_strings) is expected


class TestEndpointPermsGroup3(TestEndpointPerms):
    """group=Image OR News Item"""

    url = "/@solr?q=chomsky&group_select=3"

    @pytest.mark.parametrize(
        "role,path,expected",
        [
            ("anonymous", "/plone/noamchomsky", True),
            ("anonymous", "/plone/mynews", True),
            ("anonymous", "/plone/chomskysdocument", False),
            ("member", "/plone/noamchomsky", True),
            ("member", "/plone/mynews", True),
            ("member", "/plone/chomskysdocument", False),
            ("manager", "/plone/noamchomsky", True),
            ("manager", "/plone/mynews", True),
            ("manager", "/plone/chomskysdocument", False),
        ],
    )
    def test_paths(
        self,
        api_request,
        all_path_string,
        role: str,
        path: str,
        expected: bool,
    ):
        data = api_request(role).get(self.url).json()
        path_strings = all_path_string(data)
        assert (path in path_strings) is expected


class TestEndpointPermsGroup4(TestEndpointPerms):
    """group=Page OR News Item"""

    url = "/@solr?q=chomsky&group_select=4"

    @pytest.mark.parametrize(
        "role,path,expected",
        [
            ("anonymous", "/plone/noamchomsky", False),
            ("anonymous", "/plone/mynews", True),
            ("anonymous", "/plone/chomskysdocument", False),
            ("member", "/plone/noamchomsky", False),
            ("member", "/plone/mynews", True),
            ("member", "/plone/chomskysdocument", False),
            ("manager", "/plone/noamchomsky", False),
            ("manager", "/plone/mynews", True),
            ("manager", "/plone/chomskysdocument", True),
        ],
    )
    def test_paths(
        self,
        api_request,
        all_path_string,
        role: str,
        path: str,
        expected: bool,
    ):
        data = api_request(role).get(self.url).json()
        path_strings = all_path_string(data)
        assert (path in path_strings) is expected


class TestEndpointPermsGroup5(TestEndpointPerms):
    """group=Image"""

    url = "/@solr?q=chomsky&group_select=5"

    @pytest.mark.parametrize(
        "role,path,expected",
        [
            ("anonymous", "/plone/noamchomsky", True),
            ("anonymous", "/plone/mynews", False),
            ("anonymous", "/plone/chomskysdocument", False),
            ("member", "/plone/noamchomsky", True),
            ("member", "/plone/mynews", False),
            ("member", "/plone/chomskysdocument", False),
            ("manager", "/plone/noamchomsky", True),
            ("manager", "/plone/mynews", False),
            ("manager", "/plone/chomskysdocument", False),
        ],
    )
    def test_paths(
        self,
        api_request,
        all_path_string,
        role: str,
        path: str,
        expected: bool,
    ):
        data = api_request(role).get(self.url).json()
        path_strings = all_path_string(data)
        assert (path in path_strings) is expected
