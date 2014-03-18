# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time

from nose.plugins.attrib import attr

from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.common_utils import by_css
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from pages.loginpage.login_page import login
from pages.activitylogpage.show_activity_log_page import ShowActivityLogPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from testdata.test_data import DATA_WINNER_USER_ACTIVITY_LOG_PAGE, LOGOUT
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.activitylogtests.show_activity_log_data import *
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from tests.registrationtests.registration_tests import register_and_get_email
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from framework.utils.database_manager_postgres import DatabaseManager


class TestShowActivityLog(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation_page = login(cls.driver)
        cls.project_title = cls.create_new_project()
        cls.email = None

    @classmethod
    def create_new_project(cls):
        dashboard = cls.global_navigation_page.navigate_to_dashboard_page()
        questionnaire_creation_options_page = dashboard.navigate_to_create_project_page()
        create_questionnaire_page = questionnaire_creation_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(NEW_PROJECT_DATA, QUESTIONNAIRE_DATA)
        create_questionnaire_page.save_and_create_project_successfully()
        cls.driver.wait_for_page_with_title(5, 'Questionnaires - Overview')
        return ProjectOverviewPage(cls.driver).get_project_title()

    @attr('functional_test')
    def test_should_match_created_project_entry_in_user_activity_log_page(self):
        """
        This function will create a project and will check the user activity log entry for that action
        """

        activity_log_page = self.navigate_to_activity_log_page()
        self.assertEqual(ACTIVITY_LOG_PAGE_TITLE, self.driver.get_title())
        activity_log_page.select_filter("Project", "Created Project")
        time.sleep(3)
        for i in range(1, 10):
            if activity_log_page.get_data_on_cell(i, 3).lower() == self.project_title:
                row_index = i
                break;
        self.assertTrue(row_index >= 0, "Project title not found in activity log")
        self.assertEqual(activity_log_page.get_data_on_cell(row_index, 1), TESTER_NAME)
        self.assertEqual(activity_log_page.get_data_on_cell(row_index, 2), CREATED_PROJECT_ACTION)

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

    @classmethod
    def prepare_data_for_showing_only_logs_for_current_organization(cls):
        confirmation_page, cls.email = register_and_get_email(cls.driver)
        account_activate_page = ActivateAccountPage(cls.driver)
        dbmanager = DatabaseManager()
        activation_code = dbmanager.get_activation_code(cls.email.lower())
        account_activate_page.activate_account(activation_code)

    def assert_there_is_no_entry(self, activity_log_page):
        entries_number = activity_log_page.get_number_of_entries_found()
        self.assertEqual(0, entries_number)

    def assert_there_is_entries_for_tester150411_organization(self):
        self.driver.go_to(LOGOUT)
        login(self.driver, VALID_CREDENTIALS)
        activity_log_page = self.navigate_to_activity_log_page()
        entries_number = activity_log_page.get_number_of_entries_found()
        self.assertTrue(entries_number != 0)

    @attr('functional_test')
    def test_edit_submissions_are_logged(self):
        project_overview = self.global_navigation_page.navigate_to_view_all_project_page().navigate_to_project_overview_page(
            self.project_title)
        web_submission_page = project_overview.navigate_to_web_questionnaire_page()
        web_submission_page.fill_and_submit_answer(VALID_ANSWERS)
        time.sleep(5)
        submission_log_page = web_submission_page.navigate_to_submission_log()
        #self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".blockUI"), True)
        #self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".blockUI"))
        time.sleep(3)
        submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(EDIT_BUTTON)
        edit_submission_page = WebSubmissionPage(self.driver)
        edit_submission_page.fill_and_submit_answer(EDITED_ANSWERS)
        self.driver.wait_for_element(5, by_css('.success-message-box'), want_visible=True)
        activity_log_page = self.navigate_to_activity_log_page()
        activity_log_page.select_filter('Data Submissions', 'Edited Data Submission(s)')
        time.sleep(3)
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

    @classmethod
    def tearDownClass(cls):
        if cls.email is not None:
            dbmanager = DatabaseManager()
            dbname = dbmanager.delete_organization_all_details(cls.email.lower())
            couchwrapper = CouchHttpWrapper()
            couchwrapper.deleteDb(dbname)
        teardown_driver(cls.driver)

