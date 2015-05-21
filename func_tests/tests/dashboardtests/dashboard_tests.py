from nose.plugins.attrib import attr
import uuid
from django.test import Client
from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.logintests.login_data import VALID_CREDENTIALS
from pages.dashboardpage.dashboard_page import DashboardPage


class TestDashboard(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.client = Client()
        cls.dashboard_page = cls.login_with(credential=VALID_CREDENTIALS)

    @classmethod
    def login_with(cls, credential):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(credential)
        return DashboardPage(cls.driver)

    @attr('functional_test')
    def test_should_open_video_in_lightbox(self):
        self.assertFalse(self.dashboard_page.is_lightbox_open())
        self.dashboard_page.open_take_a_tour_video()
        self.assertTrue(self.dashboard_page.is_lightbox_open())
        self.dashboard_page.close_lightbox()
        self.assertFalse(self.dashboard_page.is_lightbox_open())
        self.dashboard_page.open_get_started_video()
        self.assertTrue(self.dashboard_page.is_lightbox_open())
        self.dashboard_page.close_lightbox()


    @attr('functional_test')
    def test_should_show_help_element_just_once(self):
        self.assertTrue(self.dashboard_page.is_help_element_present())
        self.dashboard_page.close_help_element()
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        dashboard_page = login_page.do_successful_login_with(VALID_CREDENTIALS)
        self.assertFalse(self.dashboard_page.is_help_element_present())

