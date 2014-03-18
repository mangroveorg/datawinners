# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import login
from tests.logintests.login_data import VALID_CREDENTIALS, DATA_SENDER_CREDENTIALS
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.alldatapage.all_data_page import AllDataPage


class TestAllData(HeadlessRunnerTest):
    def setUp(self):
        self.global_navigation = GlobalNavigationPage(self.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    @attr('functional_test')
    def test_should_not_display_all_failed_submission_link_for_a_simple_datasender(self):
        login(self.driver, DATA_SENDER_CREDENTIALS)
        all_data_page = AllDataPage(self.driver)
        link_exists = all_data_page.has_all_failed_submission_link()
        self.assertFalse(link_exists)

    @attr('functional_test')
    def test_should_display_all_failed_submission_link_for_an_user_account(self):
        login(self.driver, VALID_CREDENTIALS)
        all_data_page = self.global_navigation.navigate_to_all_data_page()
        link_exists = all_data_page.has_all_failed_submission_link()
        self.assertTrue(link_exists)