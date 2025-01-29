import pytest


class TestEndpointDefault:
    @pytest.fixture(autouse=True)
    def _init(self, portal_with_content, manager_request):
        self.portal = portal_with_content
        response = manager_request.get(self.url)
        self.data = response.json()

    def func(data: dict) -> list[str]:
        return [item["path_string"] for item in data["response"]["docs"]]

    url = "/@solr?q=chomsky"


class TestHighlighting(TestEndpointDefault):
    @pytest.mark.parametrize(
        "path,highlight_field,highlight",
        [
            (
                "/plone/mydocument",
                "highlighting",
                ["This is a description about <em>Chomsky</em>"],
            ),
            (
                "/plone/noamchomsky",
                "highlighting",
                None,
            ),
            (
                "/plone/mynews",
                "highlighting",
                ["Some more news about <em>Chomsky</em>"],
            ),
            (
                "/plone/myotherfolder",
                "highlighting",
                ["Container for material about <em>Chomsky</em>"],
            ),
        ],
    )
    def test_highlight_field(
        self, path: str, highlight_field: str, highlight: str
    ):
        filtered = [
            item.get(highlight_field, None)
            for item in self.data["response"]["docs"]
            if item["path_string"] == path
        ]
        assert (filtered[0] if len(filtered) > 0 else None) == highlight
