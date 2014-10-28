from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_id, by_css
from pages.loginpage.login_page import login
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from tests.websubmissiontests.web_submission_data import NEW_PROJECT_DATA, QUESTIONNAIRE_DATA, VALID_ANSWER, EDIT_BUTTON, \
    EDITED_ANSWERS


class TestWebSubmissionOnBehalfOfAnotherDatasender(HeadlessRunnerTest):

    @classmethod
    def setUpClass(self):
        HeadlessRunnerTest.setUpClass()
        self.global_navigation_page = login(self.driver)
        self.project_overview_page = self.create_new_project()

    @classmethod
    def create_new_project(self):
        dashboard = self.global_navigation_page.navigate_to_dashboard_page()
        questionnaire_creation_options_page = dashboard.navigate_to_create_project_page()
        create_questionnaire_page = questionnaire_creation_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(NEW_PROJECT_DATA, QUESTIONNAIRE_DATA)
        create_questionnaire_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(5, 'Questionnaires - Overview')
        return ProjectOverviewPage(self.driver)



    def test_to_submit_data_on_behalf_of_another_datasender(self):
        datasender = "rep11"
        edited_datsender_to = 'rep10'
        web_submission_page = self.project_overview_page.navigate_to_web_questionnaire_page()
        web_submission_page.select_checkbox_to_submit_on_behalf()
        web_submission_page.change_datasender(datasender)
        web_submission_page.fill_and_submit_answer(VALID_ANSWER)
        submission_log_page = web_submission_page.navigate_to_submission_log()
        submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(EDIT_BUTTON)
        edit_submission_page = WebSubmissionPage(self.driver)
        edit_submission_page.click_on_change_ds_link()
        edit_submission_page.change_datasender(edited_datsender_to)
        edit_submission_page.save_change_datasender()
        edit_submission_page.fill_and_submit_answer(EDITED_ANSWERS)
        self.driver.wait_for_element(5, by_css('.success-message-box'), want_visible=True)
        submission_log_page = edit_submission_page.navigate_to_submission_log()
        submission_log_page.get_total_number_of_rows()
        datasender_name = submission_log_page.get_cell_value(1, 2)
        edited_value = submission_log_page.get_cell_value(1, 5)
        status = submission_log_page.get_cell_value(1, 4)
        self.assertEquals('stefan rep10', datasender_name)
        self.assertEquals('4.0', edited_value)
        self.assertEquals('Success', status)
