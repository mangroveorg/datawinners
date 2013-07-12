# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time

from nose.plugins.attrib import attr

from framework.base_test import BaseTest
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.loginpage.login_page import LoginPage
from pages.activitylogpage.show_activity_log_page import ShowActivityLogPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_USER_ACTIVITY_LOG_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.activitylogtests.show_activity_log_data import *
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from tests.projectquestionnairetests.project_questionnaire_data import VALID_SUMMARY_REPORT_DATA
from tests.registrationtests.registration_tests import register_and_get_email
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from framework.utils.database_manager_postgres import DatabaseManager


@attr('suit_1')
class TestShowActivityLog(BaseTest):
    def login(self, credential=VALID_CREDENTIALS):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(credential)
        return DashboardPage(self.driver)


    def create_a_project_and_navigate_to_activity_log_page(self):
        dashboard = self.login()
        create_project_page = dashboard.navigate_to_create_project_page()
        create_project_page.create_project_with(VALID_SUMMARY_REPORT_DATA)
        create_project_page.continue_create_project()
        create_project_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(15, 'Projects - Overview')
        overview_page = ProjectOverviewPage(self.driver)
        self.project_title = overview_page.get_project_title()
        return self.navigate_to_activity_log_page()

    @attr('functional_test', 'smoke')
    def test_should_match_created_project_entry_in_user_activity_log_page(self):
        """
        This function will create a project and will check the user activity log entry for that action
        """
        activity_log_page = self.create_a_project_and_navigate_to_activity_log_page()
        self.assertEqual(ACTIVITY_LOG_PAGE_TITLE, self.driver.get_title())
        project_title = activity_log_page.get_data_on_cell(1, 3)
        self.assertEqual(project_title.lower(), self.project_title)
        self.assertEqual(activity_log_page.get_data_on_cell(1, 1), TESTER_NAME)
        self.assertEqual(activity_log_page.get_data_on_cell(1, 2), CREATED_PROJECT_ACTION)

    @attr('functional_test')
    def test_should_only_show_logs_for_current_organization(self):
        self.prepare_data_for_showing_only_logs_for_current_organization()
        activity_log_page = self.navigate_to_activity_log_page()
        self.assert_there_is_no_entry(activity_log_page)
        activity_log_page.click_on_filter_button()
        self.assert_there_is_no_entry(activity_log_page)
        self.assert_there_is_entries_for_tester150411_organization()


    def navigate_to_activity_log_page(self):
        self.driver.go_to(DATA_WINNER_USER_ACTIVITY_LOG_PAGE)
        return ShowActivityLogPage(self.driver)

    def prepare_data_for_showing_only_logs_for_current_organization(self):
        confirmation_page, email = register_and_get_email(self.driver)
        account_activate_page = ActivateAccountPage(self.driver)
        dbmanager = DatabaseManager()
        activation_code = dbmanager.get_activation_code(email.lower())
        account_activate_page.activate_account(activation_code)

    def assert_there_is_no_entry(self, activity_log_page):
        entries_number = activity_log_page.get_number_of_entries_found()
        self.assertEqual(0, entries_number)

    def assert_there_is_entries_for_tester150411_organization(self):
        self.driver.go_to('http://localhost:8000/logout/')
        self.login()
        activity_log_page = self.navigate_to_activity_log_page()
        entries_number = activity_log_page.get_number_of_entries_found()
        self.assertTrue(entries_number != 0)

    def test_edit_submissions_are_logged(self):
        dashboard = self.login()
        create_project_page = dashboard.navigate_to_create_project_page()
        create_project_page.create_project_with(NEW_PROJECT_DATA)
        create_project_page.continue_create_project()
        questionnaire_page = CreateQuestionnairePage(self.driver)
        questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA)
        questionnaire_page.save_and_create_project()
        project_overview = ProjectOverviewPage(self.driver)

        web_submission_page = project_overview.navigate_to_data_page().navigate_to_web_submission_tab()
        web_submission_page.fill_and_submit_answer(VALID_ANSWERS)
        submission_log_page = web_submission_page.navigate_to_submission_log()
        submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(EDIT_BUTTON)
        edit_submission_page = WebSubmissionPage(self.driver)
        edit_submission_page.fill_and_submit_answer(EDITED_ANSWERS)
        time.sleep(3)
        activity_log_page = self.navigate_to_activity_log_page()
        self.assertEqual("Edited Data Submission(s)", activity_log_page.get_data_on_cell(row=1, column=2))
        self.assertTrue(activity_log_page.get_data_on_cell(row=1, column=3).startswith("Reporter activities"))
        details_data = activity_log_page.get_data_on_cell(row=1, column=4)
        self.assertTrue("Submission Received on" in details_data)
        self.assertTrue("Changed Answers" in details_data)
        self.assertFalse("Changed Status" in details_data)
        self.assertTrue('Number of Docs: "5.0" to "4.0"' in details_data)
        self.assertTrue('Date of report: "12.01.2013" to "11.01.2013"' in details_data)
        self.assertTrue('Color of Eyes: "LIGHT RED" to "LIGHT YELLOW"' in details_data)
        self.assertTrue('Clinic admin name: "something" to "nothing"' in details_data)
        self.assertTrue('Bacterias in water: "Bacteroids" to "Aquificae, Bacteroids, Chlorobia"' in details_data)
        self.assertTrue('Geo points of Clinic: "-1,-1" to "1,1"' in details_data)
