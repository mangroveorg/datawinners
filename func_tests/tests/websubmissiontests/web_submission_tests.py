from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_, from_
from framework.base_test import HeadlessRunnerTest
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from tests.websubmissiontests.web_submission_data import *
from tests.logintests.login_data import VALID_CREDENTIALS


class TestWebSubmission(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver, VALID_CREDENTIALS)

    dashboard_page = None

    def submit_web_submission(self):
        web_submission_page = self.navigate_to_web_submission()
        self.driver.wait_for_page_with_title(5,web_submission_page.get_title())
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS)
        web_submission_page.submit_answers()
        return web_submission_page

    def navigate_to_web_submission(self):
        all_data_page = (GlobalNavigationPage(self.driver)).navigate_to_all_data_page()
        return all_data_page.navigate_to_web_submission_page(
            fetch_(PROJECT_NAME, from_(DEFAULT_ORG_DATA)))

    @attr('functional_test')
    def test_successful_web_submission_by_paid_account(self):
        web_submission_page = self.submit_web_submission()
        self.assertEqual(web_submission_page.get_errors(),[])
        self.assertEqual(web_submission_page.get_text_value('NA'), u'')

    @attr('functional_test')
    def test_paid_account_can_do_submission_after_submission_limit(self):
        web_submission_page = self.submit_web_submission()
        self.assertEqual(web_submission_page.get_errors(),[])

    @attr('functional_test')
    def test_should_check_each_questions_has_instruction(self):
        web_submission_page = self.navigate_to_web_submission()
        self.driver.wait_for_page_with_title(5, web_submission_page.get_title())
        questions, instructions = web_submission_page.get_questions_and_instructions()
        self.assertEqual(questions[2], u"What is age \xf6f father?")
        self.assertEqual(instructions[2], "Answer must be a number between 18-100.")
