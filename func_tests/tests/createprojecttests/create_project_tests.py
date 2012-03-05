# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.createprojecttests.create_project_data import *

@attr('suit_1')
class TestCreateProject(BaseTest):
    def prerequisites_of_create_project(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        dashboard_page = DashboardPage(self.driver)

        # going on setup project page
        return dashboard_page.navigate_to_create_project_page()

    @attr('functional_test', 'smoke')
    def test_successful_project_creation(self):
        """
        Function to test the successful creation of project with given
        details e.g. Name, Project Background and goal, Project Type,
        Subject and Devices
        """
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()
        create_project_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(15, fetch_(PAGE_TITLE, from_(VALID_DATA)))
        self.assertEqual(self.driver.get_title(),
                                 fetch_(PAGE_TITLE, from_(VALID_DATA)))

    @attr('functional_test')
    def test_create_project_without_entering_data(self):
        """
        Function to test the error message on the set up project page while
        creation of project
        """
        create_project_page = self.prerequisites_of_create_project()
        create_project_page.continue_create_project()
        self.assertEqual(create_project_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(BLANK_FIELDS)))
