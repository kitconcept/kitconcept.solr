from kitconcept.solr import PACKAGE_NAME
from plone import api

import pytest


class TestSetupInstall:
    def test_addon_installed(self, installer):
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1000"

    def test_browserlayer(self, browser_layers):
        """Test that IKitconceptSolrLayer is registered."""
        from kitconcept.solr.interfaces import IKitconceptSolrLayer

        assert IKitconceptSolrLayer in browser_layers

    @pytest.mark.parametrize("package_name", ["collective.solr"])
    def test_dependency_installed(self, installer, package_name):
        """Test dependencies are installed."""
        assert installer.is_product_installed(package_name) is True

    @pytest.mark.parametrize(
        "key,expected",
        [
            ["collective.solr.host", "127.0.0.1"],
            ["collective.solr.port", 8983],
            ["collective.solr.base", "/solr/plone"],
        ],
    )
    def test_registry_keys(self, portal, key, expected):
        """Test if registry keys are set."""
        value = api.portal.get_registry_record(key, default=None)
        assert value == expected

    @pytest.mark.parametrize(
        "item",
        [
            "UID",
            "Title",
            "Description",
            "Type",
            "effective",
            "start",
            "created",
            "end",
            "path_string",
            "mime_type",
            "location",
            "image_scales",
            "image_field",
        ],
    )
    def test_solr_config_fieldlist(self, portal, item):
        key = "kitconcept.solr.config"
        values = api.portal.get_registry_record(key)["fieldList"]
        assert item in values

    def test_solr_config_search_tabs(self, portal):
        key = "kitconcept.solr.config"
        config = api.portal.get_registry_record(key, default=None)
        values = config["searchTabs"]
        assert len(values) == 5
        assert values[0]["label"] == "All"
        assert values[0]["filter"] == "Type(*)"
