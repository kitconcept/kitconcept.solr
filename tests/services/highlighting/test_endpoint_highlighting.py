import pytest


class TestEndpointDefault:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()

    def func(data: dict) -> list[str]:
        return [item["path_string"] for item in data["response"]["docs"]]


class TestEndpointDefaultHighlighting(TestEndpointDefault):
    url = "/@solr?q=chomsky"

    expected = (
        ("/plone/mydocument", "highlight", None),
        ("/plone/noamchomsky", "highlight", None),
        ("/plone/mynews", "highlight", None),
    )

    def get_highlight_field(
        self, data: list, path: str, highlight_field: str
    ) -> list[str] | None:
        filtered = [
            item.get(highlight_field, None)
            for item in data["response"]["docs"]
            if item["path_string"] == path
        ]
        return filtered[0] if len(filtered) > 0 else None

    def test_paths(self):
        for path, highlight_field, highlight in self.expected:
            assert (
                self.get_highlight_field(self.data, path, highlight_field)
                == highlight
            )
