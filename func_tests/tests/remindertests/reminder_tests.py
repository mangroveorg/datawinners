from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.createprojecttests.create_project_data import VALID_DATA
from tests.logintests.login_data import TRIAL_CREDENTIALS_VALIDATES
from tests.remindertests.reminder_data import WARNING_MESSAGE
from nose.plugins.skip import SkipTest

class TestReminderSend(BaseTest):
    def login_with(self, account):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(account)
        dashboard_page = DashboardPage(self.driver)
        return dashboard_page

    def start_create_normal_project(self):
        dashboard_page = self.login_with(TRIAL_CREDENTIALS_VALIDATES)
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(VALID_DATA).continue_create_project()
        return create_project_page.save_and_create_project_successfully()

#    @attr("functional_test")
#    def test_trial_account_should_see_reminder_not_work_message_when_creating_project(self):
#        project_overview_page = self.start_create_normal_project()
#        reminder_page = project_overview_page.navigate_to_reminder_page()
#
#        self.assertEqual(WARNING_MESSAGE, message)

    def active_project_and_go_to_all_reminder_page(self, project_overview_page):
        light_box = project_overview_page.open_activate_project_light_box()
        project_overview_page = light_box.activate_project()
        return project_overview_page.navigate_to_reminder_page()

    @SkipTest
    @attr("functional_test")
    def test_trial_account_should_see_reminder_not_work_message_at_reminder_tab_in_active_project(self):
        project_overview_page = self.start_create_normal_project()
        self.active_project_and_go_to_all_reminder_page(project_overview_page)
        message = self.driver.find(REMINDER_NOT_WORK_FOR_TRIAL_MSG).text
        self.assertEqual(WARNING_MESSAGE, message)

    @SkipTest
    @attr("functional_test")
    def test_trial_account_should_see_reminder_not_work_message_at_sent_tab_in_active_project(self):
        project_overview_page = self.start_create_normal_project()
        all_reminders_page = self.active_project_and_go_to_all_reminder_page(project_overview_page)
        all_reminders_page.click_sent_reminder_tab()
        message = self.driver.find(REMINDER_NOT_WORK_FOR_TRIAL_MSG).text
        self.assertEqual(WARNING_MESSAGE, message)



