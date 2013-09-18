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

    @attr('functional_test')
    def test_should_check_instruction_for_telephone_number_question(self):
        self.prerequisites_of_edit_subject_registration_form()
        subjects_page = self.project_overview_page.navigate_to_subjects_page()
        subjects_page.navigate_to_subject_registration_form_tab()
        subjects_page.click_edit_form_link_and_continue()
        subjects_page.click_add_question_link()
        subjects_page.choose_question_type("telephone_number")
        self.assertEqual(u'Answer must be country code plus telephone number. Example: 261333745269', subjects_page.get_instruction_for_current_question())
