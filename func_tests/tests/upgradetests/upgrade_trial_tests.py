from nose.plugins.attrib import attr

from pages.upgradepage.upgrade_page import UpgradePage
from tests.endtoendtest.end_to_end_tests import add_trial_organization_and_login
from upgrade_trial_data import *
from framework.base_test import HeadlessRunnerTest
from testdata.test_data import UPGRADE_PAGE, LOGOUT, DATA_WINNER_DASHBOARD_PAGE


class TestUpgradePage(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()

    def tearDown(self):
        self.driver.go_to(LOGOUT)

    @attr('functional_test')
    def test_upgrade_page_error(self):
        add_trial_organization_and_login(self.driver)
        self.driver.go_to(UPGRADE_PAGE)
        upgrade_page = UpgradePage(self.driver)
        upgrade_page.register_with(INVALID_DATA)
        self.assertEquals(upgrade_page.get_error_message(), INVALID_DATA_ERROR_MESSAGE)
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        self.driver.go_to(UPGRADE_PAGE)
        upgrade_page.register_with(INVALID_DATA2)
        self.assertEquals(upgrade_page.get_error_message(), INVALID_DATA2_ERROR_MESSAGE)
