# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.loginpage.login_page import LoginPage
from pages.activitylogpage.show_activity_log_page import ShowActivityLogPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_USER_ACTIVITY_LOG_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.activitylogtests.show_activity_log_data import *
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from tests.createprojecttests.create_project_data import VALID_DATA, PAGE_TITLE as PROJECT_OVERVIEW_PAGE_TITLE

@attr('suit_1')
class TestShowActivityLog(BaseTest):
    def login(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        return DashboardPage(self.driver)
        

    def create_a_project_and_navigate_to_activity_log_page(self):
        dashboard = self.login()
        create_project_page = dashboard.navigate_to_create_project_page()
        create_project_page.create_project_with(VALID_DATA)
        create_project_page.continue_create_project()
        create_project_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(15, VALID_DATA.get(PROJECT_OVERVIEW_PAGE_TITLE))
        overview_page = ProjectOverviewPage(self.driver)
        self.project_title = overview_page.get_project_title()
        self.driver.go_to(DATA_WINNER_USER_ACTIVITY_LOG_PAGE)
        return ShowActivityLogPage(self.driver)

    @attr('functional_test', 'smoke')
    def test_should_match_created_project_entry_in_user_activity_log_page(self):
        """
        This function will create a project and will check the user activity log entry for that action
        """
        activity_log_page = self.create_a_project_and_navigate_to_activity_log_page()
        self.assertEqual(PAGE_TITLE, self.driver.get_title())
        project_title = activity_log_page.get_data_on_cell(1,3)
        self.assertEqual(project_title.lower(), self.project_title)
        self.assertEqual(activity_log_page.get_data_on_cell(1,1), TESTER_NAME)
        self.assertEqual(activity_log_page.get_data_on_cell(1,2), CREATED_PROJECT_ACTION)
        

