# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from tribuna.annotator.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of tribuna.annotator into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if tribuna.annotator is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('tribuna.annotator'))

    def test_uninstall(self):
        """Test if tribuna.annotator is cleanly uninstalled."""
        self.installer.uninstallProducts(['tribuna.annotator'])
        self.assertFalse(self.installer.isProductInstalled('tribuna.annotator'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ITribunaAnnotatorLayer is registered."""
        from tribuna.annotator.interfaces import ITribunaAnnotatorLayer
        from plone.browserlayer import utils
        self.failUnless(ITribunaAnnotatorLayer in utils.registered_layers())
