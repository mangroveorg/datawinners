from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.addsubjecttests.add_subject_data import VALID_PROJECT_DATA, PAGE_TITLE, VALID_SUBJECT_REGISTRATION_DATA, SUCCESS_MSG
from tests.logintests.login_data import VALID_CREDENTIALS


class TestRegisterSubjectFromProject(BaseTest):
    @attr('functional_test')
    def test_successful_subject_registration(self):
        """
        Function to test the successful addition of a subject from "My Subjects" page
        with given details e.g. First Name, Last Name, Location, GPS, Mobile Number
        """

        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        dashboard_page = DashboardPage(self.driver)

        # going on setup project page
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(VALID_PROJECT_DATA)
        create_project_page.continue_create_project()
        project_overview_page = create_project_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(15, fetch_(PAGE_TITLE, from_(VALID_PROJECT_DATA)))
        self.assertEqual(self.driver.get_title(),
                         fetch_(PAGE_TITLE, from_(VALID_PROJECT_DATA)))
        project_subject_page = project_overview_page.navigate_to_subjects_page()
        project_subject_registration_page = project_subject_page.click_register_subject()
        project_subject_registration_page.add_subject_with(VALID_SUBJECT_REGISTRATION_DATA)
        project_subject_registration_page.submit_subject()
        success_message = project_subject_registration_page.get_flash_message()
        self.assertRegexpMatches(success_message, fetch_(SUCCESS_MSG, from_(VALID_SUBJECT_REGISTRATION_DATA)))