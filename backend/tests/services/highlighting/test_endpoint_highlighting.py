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
            # highlighting (content field)
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
            # highlighting_title (Title field)
            (
                "/plone/mydocument",
                "highlighting_title",
                ["My Document about Noam <em>Chomsky</em>"],
            ),
            (
                "/plone/noamchomsky",
                "highlighting_title",
                ["Prof. Dr. Noam <em>Chomsky</em>"],
            ),
            (
                "/plone/mynews",
                "highlighting_title",
                ["My News Item with Noam <em>Chomsky</em>"],
            ),
            (
                "/plone/myotherfolder",
                "highlighting_title",
                None,
            ),
            # highlighting_description (Description field)
            (
                "/plone/noamchomsky",
                "highlighting_description",
                ["The real <em>Chomsky</em> is here."],
            ),
            (
                "/plone/mydocument",
                "highlighting_description",
                None,
            ),
        ],
    )
    def test_highlight_field(self, path: str, highlight_field: str, highlight: str):
        filtered = [
            item.get(highlight_field, None)
            for item in self.data["response"]["docs"]
            if item["path_string"] == path
        ]
        assert (filtered[0] if len(filtered) > 0 else None) == highlight
