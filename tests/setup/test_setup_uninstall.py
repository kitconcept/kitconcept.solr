from kitconcept.solr import PACKAGE_NAME

import pytest


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product(PACKAGE_NAME)

    def test_product_uninstalled(self, installer):
        """Test if kitconcept.solr is cleanly uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False

    def test_browserlayer_removed(self, browser_layers):
        """Test that IKitconceptSolrLayer is removed."""
        from kitconcept.solr.interfaces import IKitconceptSolrLayer

        assert IKitconceptSolrLayer not in browser_layers
