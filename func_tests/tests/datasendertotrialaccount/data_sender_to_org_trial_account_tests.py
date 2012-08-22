from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_LOGIN_PAGE
from framework.base_test import BaseTest
from data_sender_to_org_trial_account_data import VALID_DATA, PROJECT_NAME, TRIAL_SMS_DATA, VALID_PAID_DATA, PAID_SMS_DATA
from pages.loginpage.login_page import LoginPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from tests.logintests.login_data import TRIAL_CREDENTIALS_VALIDATES, VALID_CREDENTIALS, TRIAL_CREDENTIALS_THREE
from nose.plugins.attrib import attr
from framework.utils.couch_http_wrapper import CouchHttpWrapper
import json
from nose.plugins.skip import SkipTest


# add data sender to trial account

# add data sender to paid account

# send sms to trial one
    #check sms submission in this trail display, not paid display

# send sms to paid account
    #check sms submission paid paid display, not paid display

@attr('suit_2')
class TestDataSenderAssociationWithTrialAccount(BaseTest):

    @attr('functional_test', 'smoke')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_trial_org_is_saved_in_trial_org(self):
        self.send_sms(VALID_DATA)
        analysis_page = self.go_to_analysis_page(TRIAL_CREDENTIALS_VALIDATES)
        data_rows = analysis_page.get_all_data_records_from_multiple_pages()
        self.assertIn(TRIAL_SMS_DATA,data_rows)

    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_trial_org_is_not_saved_in_paid_org(self):
        self.send_sms(VALID_DATA)
        analysis_page = self.go_to_analysis_page(VALID_CREDENTIALS)
        data_rows = analysis_page.get_all_data_records_from_multiple_pages()
        self.assertNotIn(TRIAL_SMS_DATA,data_rows)

    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_trial_org_is_not_saved_in_other_trial_org(self):
        self.send_sms(VALID_DATA)
        analysis_page = self.go_to_analysis_page(TRIAL_CREDENTIALS_THREE)
        data_rows = analysis_page.get_all_data_records_from_multiple_pages()
        self.assertNotIn(TRIAL_SMS_DATA,data_rows)

    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_paid_org_is_saved_in_paid_org(self):
        self.send_sms(VALID_PAID_DATA)
        analysis_page = self.go_to_analysis_page(VALID_CREDENTIALS)
        data_rows = analysis_page.get_all_data_records_from_multiple_pages()
        self.assertIn(PAID_SMS_DATA,data_rows)

    @attr('functional_test')
    def test_SMS_sent_by_data_sender_registered_for_trial_and_paid_orgs_to_paid_org_is_not_saved_in_other_orgs(self):
        self.send_sms(VALID_PAID_DATA)
        analysis_page = self.go_to_analysis_page(TRIAL_CREDENTIALS_VALIDATES)
        data_rows = analysis_page.get_all_data_records_from_multiple_pages()
        self.assertNotIn(PAID_SMS_DATA,data_rows)

    def send_sms(self, sms_content):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_sms_with(sms_content)

    def go_to_analysis_page(self, account):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(account)
        all_data_page = global_navigation.navigate_to_all_data_page()
        analysis_page = all_data_page.navigate_to_data_analysis_page(PROJECT_NAME)
        return analysis_page

    def tearDown(self):
        self.driver.close()
        couchdb_wrapper = CouchHttpWrapper("localhost")
        json_data = couchdb_wrapper.get("/hni_testorg_coj00001/_design/submissionlog/_view/submissionlog?reduce=false")
        json_parsed_data = json.load(json_data)
        for data in range(json_parsed_data["total_rows"]):
            id = json_parsed_data["rows"][data]["id"]
            rev = json_parsed_data["rows"][data]["value"]["_rev"]
            couchdb_wrapper.delete("/hni_testorg_coj00001/"+id+"?rev="+rev)
