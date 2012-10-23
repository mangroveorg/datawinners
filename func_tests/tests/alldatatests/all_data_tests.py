# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from framework.utils.data_fetcher import fetch_, from_
from framework.base_test import setup_driver, teardown_driver
from nose.plugins.attrib import attr
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS, USERNAME, PASSWORD, DATA_SENDER_CREDENTIALS
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.alldatapage.all_data_page import AllDataPage

@attr('suit_1')
class TestAllData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    def setUp(self):
        self.global_navigation = GlobalNavigationPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    def login_with(self, credential):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(credential)
        

    @attr('functional_test')
    def test_should_not_display_all_failed_submission_link_for_a_simple_datasender(self):
        self.login_with(DATA_SENDER_CREDENTIALS)
        all_data_page = AllDataPage(self.driver)
        link_exists = all_data_page.has_all_failed_submission_link()
        self.assertFalse(link_exists)

    @attr('functional_test')
    def test_should_display_all_failed_submission_link_for_an_user_account(self):
        self.login_with(VALID_CREDENTIALS)
        all_data_page = self.global_navigation.navigate_to_all_data_page()
        link_exists = all_data_page.has_all_failed_submission_link()
        self.assertTrue(link_exists)