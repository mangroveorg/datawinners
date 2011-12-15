from framework.utils.data_fetcher import fetch_, from_
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.loginpage.login_page import LoginPage
from tests.websubmissiontests.web_submission_data import *
from tests.logintests.login_data import VALID_CREDENTIALS, TRIAL_CREDENTIALS_VALIDATES
from nose.plugins.skip import SkipTest

class TestWebSubmission(BaseTest):
    dashboard_page = None

    def prerequisites_of_web_submission(self, credentials):
        login_page = LoginPage.navigate_to(self.driver)
        return login_page.do_successful_login_with(credentials)

    def submit_web_submission(self, times, credentials):
        dashboard_page = self.prerequisites_of_web_submission(credentials)
        all_data_page = dashboard_page.navigate_to_all_data_page()
        web_submission_page = all_data_page.navigate_to_web_submission_page(
            fetch_(PROJECT_NAME, from_(DEFAULT_ORG_DATA)))
        for i in range(times):
            print "Submission Number:"+str(i+1)
            web_submission_page.submit_questionnaire_with(VALID_ANSWERS)
        return web_submission_page

    @attr('functional_test')
    def test_successful_web_submission_by_paid_account(self):
        web_submission_page = self.submit_web_submission(1, VALID_CREDENTIALS)
        self.assertEqual(web_submission_page.get_errors(),[])
        
    @attr('functional_test')
    def test_paid_account_can_do_submission_after_submission_limit(self):
        web_submission_page = self.submit_web_submission(11, VALID_CREDENTIALS)
        self.assertEqual(web_submission_page.get_errors(),[])

    @SkipTest
    @attr('functional_test')
    def test_trial_account_submission_without_limit(self):
        web_submission_page = self.submit_web_submission(11, TRIAL_CREDENTIALS_VALIDATES)
        self.assertEqual(web_submission_page.get_errors(),[])

