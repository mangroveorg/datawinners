from nose.plugins.attrib import attr
import uuid
from django.test import Client
from framework.base_test import HeadlessRunnerTest
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.logintests.login_data import VALID_CREDENTIALS
from pages.dashboardpage.dashboard_page import DashboardPage
from tests.dashboardtests.dashboard_tests_data import *


class TestDashboard(HeadlessRunnerTest):
    def setUp(self):
        self.client = Client()
        self.dashboard_page = self.login_with(credential=VALID_CREDENTIALS)

    def tearDown(self):
        self.driver.go_to(LOGOUT)

    @classmethod
    def login_with(self, credential):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(credential)
        return DashboardPage(self.driver)

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


    @attr('functional_test')
    def test_should_restrict_questionnaire_list_on_dashboard_according_to_user_permission(self):
        self.assertGreaterEqual(len(self.dashboard_page.get_projects_list()), 8)
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(USER_RASITEFA_CREDENTIALS)
        self.assertEqual(len(self.dashboard_page.get_projects_list()), 5)

    @attr('functional_test')
    def test_should_available_project_for_send_sms(self):
        send_sms_lightbox = self.dashboard_page.click_on_send_a_message()
        all_questionnaires = send_sms_lightbox.get_all_available_questionnaires()
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(USER_RASITEFA_CREDENTIALS)
        send_sms_lightbox = self.dashboard_page.click_on_send_a_message()
        questionnaires = send_sms_lightbox.get_all_available_questionnaires()
        self.driver.create_screenshot('show-questionnaire-for-rasitefa')
        self.assertGreater(len(all_questionnaires), len(questionnaires))
        self.assertEqual(len(questionnaires), 5)
