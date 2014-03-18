from unittest import SkipTest
from nose.plugins.attrib import attr

from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_LOGIN_PAGE, LOGOUT

from framework.base_test import BaseTest, HeadlessRunnerTest
from data_sender_to_org_trial_account_data import VALID_DATA, PROJECT_NAME, VALID_PAID_DATA, \
    RE_TRIAL_SMS_DATA, RE_PAID_SMS_DATA
from pages.loginpage.login_page import LoginPage, login
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from tests.logintests.login_data import TRIAL_CREDENTIALS_VALIDATES, VALID_CREDENTIALS
from tests.submissionlogtests.submission_log_tests import send_valid_sms_with


''' usecase : Two organisations have datasender with same mobile number.
 This test tests that submissions made through sms reach the accounts based on the receiver end points'''


class TestDataSenderAssociationWithTrialAccount(HeadlessRunnerTest):

    def tearDown(self):
        self.driver.go_to(LOGOUT)

    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_trial_org_is_saved_in_right_trial_org(self):
        send_valid_sms_with(VALID_DATA)
        analysis_page = self.go_to_analysis_page(TRIAL_CREDENTIALS_VALIDATES)
        first_submission = analysis_page.get_all_data_on_nth_row(1)
        self.assertRegexpMatches(' '.join(first_submission), RE_TRIAL_SMS_DATA)
        self.driver.go_to(LOGOUT)

        analysis_page = self.go_to_analysis_page(VALID_CREDENTIALS)
        first_submission = analysis_page.get_all_data_on_nth_row(1)
        self.assertNotRegexpMatches(' '.join(first_submission), RE_TRIAL_SMS_DATA)
        self.driver.go_to(LOGOUT)

    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_paid_org_is_saved_in_paid_org(self):
        send_valid_sms_with(VALID_PAID_DATA)
        analysis_page = self.go_to_analysis_page(VALID_CREDENTIALS)
        first_submission = analysis_page.get_all_data_on_nth_row(1)
        self.assertRegexpMatches(' '.join(first_submission), RE_PAID_SMS_DATA)
        self.driver.go_to(LOGOUT)

        analysis_page = self.go_to_analysis_page(TRIAL_CREDENTIALS_VALIDATES)
        first_submission = analysis_page.get_all_data_on_nth_row(1)
        self.assertNotRegexpMatches(' '.join(first_submission), RE_PAID_SMS_DATA)

    def go_to_analysis_page(self, credentials):
        global_navigation = login(self.driver, credentials)
        all_data_page = global_navigation.navigate_to_all_data_page()
        analysis_page = all_data_page.navigate_to_data_analysis_page(PROJECT_NAME)
        analysis_page.wait_for_table_data_to_load()
        return analysis_page
