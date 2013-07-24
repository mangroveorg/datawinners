import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.common_utils import by_css
from pages.loginpage.login_page import LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.smstestertests.sms_tester_data import MESSAGE
from tests.submissionlogtests.edit_survey_response_data import get_sms_data_with_questionnaire_code
from tests.submissionlogtests.edit_survey_response_tests import submit_sms_data, navigate_to_submission_log_page_from_project_dashboard, create_project


class ProjectActivationTests(unittest.TestCase):
    def setUp(self):
        self.driver = setup_driver()
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

    def tearDown(self):
        teardown_driver(self.driver)

    @attr('functional_test', 'smoke')
    def test_deleted_project_not_visible(self):
        project_overview_page = create_project(self.driver)
        project_name = project_overview_page.get_project_title()
        project_page = self.global_navigation.navigate_to_view_all_project_page()
        self.assertTrue(project_page.is_project_present(project_name))

        project_page.delete_project(project_name)
        self.assertFalse(project_page.is_project_present(project_name))

    @attr('functional_test', 'smoke')
    def test_should_delete_submissions_after_activating_project(self):
        project_overview_page = create_project(self.driver)
        project_name = project_overview_page.get_project_title()
        questionnaire_code = project_overview_page.get_questionnaire_code()

        sms_data = get_sms_data_with_questionnaire_code(questionnaire_code)
        page_message = submit_sms_data(self.driver, sms_data)
        self.assertEqual(page_message, sms_data[MESSAGE])

        submission_log_page = navigate_to_submission_log_page_from_project_dashboard(self.driver,
                                                                                     project_name=project_name)
        self.assertTrue(submission_log_page.get_total_count_of_records() >= 1)
        self.driver.find(by_css('.activate_project')).click()
        self.driver.find(by_css('#confirm')).click()
        project_overview_page = ProjectOverviewPage(self.driver)
        self.assertEquals('Active', project_overview_page.get_status_of_the_project())
        analysis_page = project_overview_page.navigate_to_data_page()
        msg = u"Your Data Senders\u2019 successful submissions will appear here"
        self.assertIn(msg, analysis_page.get_all_data_records()[0])
        submission_log_page = analysis_page.navigate_to_all_data_record_page()
        msg = "Once your Data Senders have sent in Submissions, they will appear here."
        self.assertIn(msg, submission_log_page.empty_help_text())

