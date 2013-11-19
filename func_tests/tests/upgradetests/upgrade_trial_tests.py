import unittest
from nose.plugins.attrib import attr
from pages.upgradepage.upgrade_page import UpgradePage
from upgrade_trial_data import *
from framework.base_test import setup_driver, teardown_driver
from testdata.test_data import UPGRADE_PAGE, DATA_WINNER_LOGIN_PAGE, DATA_WINNER_REGISTER_PAGE
from pages.loginpage.login_page import LoginPage
from tests.logintests.login_data import *
from django.contrib.auth.models import User
from framework.utils.data_fetcher import *

@attr('suit_2')
class TestUpgradePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.user = User.objects.get(username=fetch_(USERNAME, from_(TRIAL_CREDENTIALS_VALIDATES)))
        cls.user.groups.add(1)
        cls.dashboard = login_page.do_successful_login_with(TRIAL_CREDENTIALS_VALIDATES)
        cls.driver.go_to(UPGRADE_PAGE)

    @classmethod
    def tearDownClass(cls):
        cls.user.groups.remove(1)
        teardown_driver(cls.driver)


    @attr('functional_test')
    def test_should_open_upgrade_page(self):
        upgrade_page = UpgradePage(self.driver)
        self.assertEqual(self.driver.get_title(), "Upgrade")

    @attr('functional_test')
    def test_upgrade_page_error(self):
        self.driver.go_to(UPGRADE_PAGE)
        upgrade_page = UpgradePage(self.driver)
        upgrade_page.register_with(INVALID_DATA)
        self.assertEquals(upgrade_page.get_error_message(), INVALID_DATA_ERROR_MESSAGE)

    @attr('functional_test')
    def test_register_ngo_with_invalid_web_url(self):
        self.driver.go_to(UPGRADE_PAGE)
        upgrade_page = UpgradePage(self.driver)
        upgrade_page.register_with(INVALID_DATA2)
        self.assertEquals(upgrade_page.get_error_message(), INVALID_DATA2_ERROR_MESSAGE)