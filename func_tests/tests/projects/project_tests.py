import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
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


