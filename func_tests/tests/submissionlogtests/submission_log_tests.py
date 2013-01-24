# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import  setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_LOGIN_PAGE, DATA_WINNER_DASHBOARD_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.smstestertests.sms_tester_data import *
from tests.submissionlogtests.submission_log_data import *
from pages.warningdialog.warning_dialog_page import WarningDialog
import time

@attr('suit_3')
class TestSubmissionLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.dashboard = login_page.do_successful_login_with(VALID_CREDENTIALS)

    def setUp(self):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        self.page = SMSTesterPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def prerequisites_of_submission_log(self, sms_data):
        sms_tester_page = self.page
        sms_tester_page.send_sms_with(sms_data)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(MESSAGE, from_(sms_data)))
        return self.navigate_to_submission_log_page()

    def navigate_to_submission_log_page(self, project_name=PROJECT_NAME):
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        view_all_project_page = self.dashboard.navigate_to_view_all_project_page()
        project_overview_project = view_all_project_page.navigate_to_project_overview_page(project_name)
        data_page = project_overview_project.navigate_to_data_page()
        submission_log_page = data_page.navigate_to_all_data_record_page()
        return submission_log_page

    @attr('functional_test')
    def test_should_show_warning_when_deleting_records(self):
        submission_log_page = self.navigate_to_submission_log_page(project_name=FIRST_PROJECT_NAME)
        time.sleep(5)
        submission_log_page.check_all_submissions()
        submission_log_page.choose_delete_on_the_action_dropdown()
        warning_dialog = WarningDialog(self.driver)
        self.assertEqual(DELETE_SUBMISSION_WARNING_MESSAGE, warning_dialog.get_message())

    @attr('functional_test')
    def test_should_sort_data_by_submission_date_by_default(self):
        submission_log_page = self.navigate_to_submission_log_page(project_name=FIRST_PROJECT_NAME)
        time.sleep(3)
        self.assertEqual(submission_log_page.get_all_data_on_nth_column(6), EXPECTED_RP_LIST)

    @attr('functional_test')
    def test_should_sort_data_alphanumerically_for_other_column_than_submission_date(self):
        submission_log_page = self.navigate_to_submission_log_page(project_name=FIRST_PROJECT_NAME)
        time.sleep(3)
        submission_log_page.click_on_nth_header(8)
        self.assertEqual(submission_log_page.get_all_data_on_nth_column(6), EXPECTED_RP_SORTED_BY_SUBJECT_LIST)
