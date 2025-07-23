from plone.app.testing import setRoles

import pytest
import transaction


@pytest.fixture()
def member_request(request_factory, user_credentials):
    request = request_factory()
    request.auth = user_credentials
    yield request
    request.auth = ()


class TestEndpointRolesAndUsers:
    url = "/@solr?q=chomsky"

    @pytest.fixture
    def api_request(self, request_factory, users_credentials_role, portal, roles):
        def func(role: str) -> dict:
            req = request_factory()
            credentials = users_credentials_role.get(role, None)
            if credentials:
                req.auth = credentials
                # setting the role is explicitly needed for these tests
                setRoles(portal, credentials[0], roles)
                transaction.commit()
            return req

        return func

    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content):
        self.portal = portal_with_content


class TestEndpointRolesAndUsersNoPermission(TestEndpointRolesAndUsers):
    @pytest.mark.parametrize(
        "role,roles,path,expected",
        [
            ("anonymous", ["Anonymous"], "/plone/document2", False),
            (
                "member_as_user1",
                ["user:test_user_1_"],
                "/plone/document2",
                True,
            ),
            ("member_as_user1", ["Reader"], "/plone/document2", True),
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
