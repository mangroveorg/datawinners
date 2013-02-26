from framework.base_test import BaseTest
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from nose.plugins.attrib import attr

class TestEditSubjectRegistrationForm(BaseTest):

    def prerequisites_of_edit_subject_registration_form(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        self.project_overview_page = all_project_page.navigate_to_project_overview_page("Clinic5 Test Project")

    def test_should_add_question_successfully(self):
        self.prerequisites_of_edit_subject_registration_form()
        subjects_page = self.project_overview_page.navigate_to_subjects_page()
        subjects_page.click_edit_form_link_and_continue()
        subjects_page.click_add_question_link()

        self.assertEqual("Question", subjects_page.get_selected_question_label())

        subjects_page.click_submit_button()
        self.assertTrue(subjects_page.is_success_message_tip_show())

    @attr("functional_test")
    def test_question_should_be_editable(self):
        self.prerequisites_of_edit_subject_registration_form()
        subjects_page = self.project_overview_page.navigate_to_subjects_page()
        subjects_page.click_edit_form_link_and_continue()
        self.assertTrue(subjects_page.is_question_type_enabled())



