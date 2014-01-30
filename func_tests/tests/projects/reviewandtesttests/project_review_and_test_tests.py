import json
import unittest
from nose.plugins.attrib import attr
from datawinners.feeds.migrate import project_by_form_model_id
from datawinners.main.database import get_db_manager
from mangrove.form_model.form_model import get_form_model_by_code
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from tests.projects.reviewandtesttests.project_review_and_test_data import *

@attr("functional_test")
class TestReminderStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    def go_to_project_review_and_test_page(self, project_name=CLINIC_REMINDER_PROJECT_NAME):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return project_overview_page.navigate_to_review_and_test()

    def test_should_delete_all_submissions_given_delete_all_flag_true(self):
        form_code = "cli001"
        self.dbm = get_db_manager('hni_testorg_slx364903')
        form_model = get_form_model_by_code(self.dbm, form_code)
        self.project = project_by_form_model_id(self.dbm, form_model.id)
        resp = self.client.get('/project/finish/' + self.project.id)
        self.assertEqual(json.loads(resp.content)['is_reminder'], "enabled")

    # def test_should_get_enabled_as_reminder_status(self):
    #     project_review = self.go_to_project_review_and_test_page()
    #     status = project_review.get_reminder_status()
    #     self.driver.create_screenshot("reminder_status.png")
    #     self.assertEqual(status, "enabled")

    def test_should_get_disabled_as_reminder_status(self):
        project_review = self.go_to_project_review_and_test_page(project_name=CLINIC_PROJECT2_NAME)
        self.assertEqual(project_review.get_reminder_status(), "disabled")

