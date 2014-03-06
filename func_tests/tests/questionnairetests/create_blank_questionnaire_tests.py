import unittest
from framework.base_test import setup_driver, teardown_driver
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS


class TestCreateBlankQuestionnaire(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_name = None
        cls.driver = setup_driver(browser="phantom")
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()


    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def test_should_not_select_any_question_by_default(self):
        select_or_add_question_message = self.create_questionnaire_page.get_select_or_edit_question_message()
        self.assertTrue(select_or_add_question_message.is_displayed(), "Select/add question text not present")

    def test_submitting_a_blank_questionnaire_should_show_error_popup(self):
        self.create_questionnaire_page.set_title("Functional test - Errored project")
        no_submission_popup = self.create_questionnaire_page.get_empty_submission_popup()
        self.assertFalse(no_submission_popup.is_displayed(), "Empty Questionnaire popup should come up only on submitting")
        self.create_questionnaire_page.submit_errored_questionnaire()
        self.assertTrue(no_submission_popup.is_displayed(), "Empty Questionnaire popup did not show up")




