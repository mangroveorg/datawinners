import unittest
from nose.plugins.attrib import attr
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from framework.base_test import setup_driver, teardown_driver
from pages.loginpage.login_page import LoginPage
from tests.projectreviewandtesttests.project_review_and_test_data import *

@attr('suit_1')
class TestRegisteredDataSenders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    def go_to_project_review_and_test_page(self, project_name=CLINIC_PROJECT1_NAME):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        all_project_page = self.global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_project_page.navigate_to_project_overview_page(project_name)
        return project_overview_page.navigate_to_review_and_test()

    @attr("functional_test21")
    def test_should_get_disabled_as_reminder_status(self):
        project_review = self.go_to_project_review_and_test_page()
        self.assertEqual(project_review.get_reminder_status(), "enabled")

    @attr("functional_test")
    def test_should_get_enbled_as_reminder_status(self):
        project_review = self.go_to_project_review_and_test_page(project_name=CLINIC_PROJECT2_NAME)
        self.assertEqual(project_review.get_reminder_status(), "disabled")

