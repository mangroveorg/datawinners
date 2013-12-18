from unittest import SkipTest
from nose.plugins.attrib import attr

from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_LOGIN_PAGE, LOGOUT

from framework.base_test import BaseTest
from data_sender_to_org_trial_account_data import VALID_DATA, PROJECT_NAME, VALID_PAID_DATA, \
    RE_TRIAL_SMS_DATA, RE_PAID_SMS_DATA
from pages.loginpage.login_page import LoginPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from tests.logintests.login_data import TRIAL_CREDENTIALS_VALIDATES, VALID_CREDENTIALS


''' usecase : Two organisations have datasender with same mobile number.
 This test tests that submissions made through sms reach the accounts based on the receiver end points'''


class TestDataSenderAssociationWithTrialAccount(BaseTest):
    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_trial_org_is_saved_in_right_trial_org(self):
        self.send_sms(VALID_DATA)
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
        self.send_sms(VALID_PAID_DATA)
        analysis_page = self.go_to_analysis_page(VALID_CREDENTIALS)
        first_submission = analysis_page.get_all_data_on_nth_row(1)
        self.assertRegexpMatches(' '.join(first_submission), RE_PAID_SMS_DATA)
        self.driver.go_to(LOGOUT)

        analysis_page = self.go_to_analysis_page(TRIAL_CREDENTIALS_VALIDATES)
        first_submission = analysis_page.get_all_data_on_nth_row(1)
        self.assertNotRegexpMatches(' '.join(first_submission), RE_PAID_SMS_DATA)

    def send_sms(self, sms_content):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_valid_sms_with(sms_content)

    def go_to_analysis_page(self, credentials):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(credentials)
        all_data_page = global_navigation.navigate_to_all_data_page()
        analysis_page = all_data_page.navigate_to_data_analysis_page(PROJECT_NAME)
        analysis_page.wait_for_table_data_to_load()
        return analysis_page
