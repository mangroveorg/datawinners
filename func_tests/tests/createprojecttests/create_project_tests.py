# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from pages.previewnavigationpage.preview_navigation_page import PreviewNavigationPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.createprojecttests.create_project_data import *
import time

#@attr('suit_1')
class TestCreateProject(BaseTest):
    def prerequisites_of_create_project(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        dashboard_page = DashboardPage(self.driver)

        # going on setup project page
        return dashboard_page.navigate_to_create_project_page()

    @attr('functional_test', 'smoke')
    def test_successful_project_creation(self):
        """
        Function to test the successful creation of project with given
        details e.g. Name, Project Background and goal, Project Type,
        Subject and Devices
        """
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()
        create_project_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(15, fetch_(PAGE_TITLE, from_(VALID_DATA)))
        self.assertEqual(self.driver.get_title(),
            fetch_(PAGE_TITLE, from_(VALID_DATA)))

    @attr('functional_test')
    def test_sms_preview_of_questionnaire_when_create_project(self):
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()

        preview_navigation_page = PreviewNavigationPage(self.driver)
        sms_questionnaire_preview_page = preview_navigation_page.sms_questionnaire_preview()

        self.assertIsNotNone(sms_questionnaire_preview_page.sms_questionnaire())
        self.assertRegexpMatches(sms_questionnaire_preview_page.get_project_name(),
            "^%s" % fetch_(PROJECT_NAME, from_(VALID_DATA)))
        self.assertIsNotNone(sms_questionnaire_preview_page.get_sms_instruction())

        sms_questionnaire_preview_page.close_preview()
        self.assertFalse(sms_questionnaire_preview_page.sms_questionnaire_exist())

    @attr('functional_test')
    def test_web_preview_of_questionnaire_when_create_project(self):
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()

        preview_navigation_page = PreviewNavigationPage(self.driver)
        web_questionnaire_preview_page = preview_navigation_page.web_questionnaire_preview()

        self.assertIsNotNone(web_questionnaire_preview_page.web_questionnaire())
        self.assertIsNotNone(web_questionnaire_preview_page.get_web_instruction())

    @attr('functional_test')
    def test_smart_phone_preview_of_questionnaire_when_create_project(self):
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()

        preview_navigation_page = PreviewNavigationPage(self.driver)
        smart_phone_instruction_page = preview_navigation_page.smart_phone_preview()
        self.assertIsNotNone(smart_phone_instruction_page.get_smart_phone_instruction())

    @attr('functional_test')
    def test_warning_message_when_Osi_change_pre_defined_periodicity_question(self):
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()
        create_project_page.select_predefined_periodicity_question_text()
        warning_message = create_project_page.get_warning_message()
        self.assertEqual(warning_message, fetch_(WARNING_MESSAGE, from_(VALID_DATA)))

    @attr('functional_test', 'smoke')
    def test_should_not_create_project_if_description_longer_than_130_chars(self):
        create_project_page = self.prerequisites_of_create_project()
        self.assertFalse(create_project_page.description_has_error())
        time.sleep(1)
        create_project_page.create_project_with(LONG_DESCRIPTION_DATA)
        create_project_page.continue_create_project()
        self.assertTrue(create_project_page.description_has_error())
    