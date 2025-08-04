import pytest


class TestEndpointContentFields:
    url: str = "@solr"

    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()


class TestEndpointContentFieldsId(TestEndpointContentFields):
    url = "/@solr?q=red"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/redandblue", True),
            ("/plone/news1", False),
            ("/plone/news2", False),
            ("/plone/news3", False),
            ("/plone/blue", False),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected

    def test_count(self):
        assert "response" in self.data
        assert self.data["response"]["numFound"] == 1


class TestEndpointContentFieldsTitle(TestEndpointContentFields):
    url = "/@solr?q=news"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/plone/redandblue", False),
            ("/plone/news1", True),
            ("/plone/news2", True),
            ("/plone/news3", True),
            ("/plone/blue", True),
        ],
    )
    def test_paths(self, all_path_string, path: str, expected: bool):
        path_strings = all_path_string(self.data)
        assert (path in path_strings) is expected

    def test_count(self):
        assert "response" in self.data
        assert self.data["response"]["numFound"] == 4

    @pytest.mark.parametrize(
        "idx,title,location",
        [
            (0, "News Item 1", ""),
            (1, "News Item 2", ""),
            (2, "News Item 3", "My location"),
            (3, "Blue news item", ""),
        ],
    )
    def test_attributes(self, idx: int, title: str, location: str):
        docs = self.data["response"]["docs"]
        item = docs[idx]
        assert item["Title"] == title
        assert item.get("location", "") == location
