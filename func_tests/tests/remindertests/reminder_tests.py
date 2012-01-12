from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.createprojectpage import create_project_page
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import TRIAL_CREDENTIALS_VALIDATES
from tests.remindertests.reminder_data import *
from nose.plugins.skip import SkipTest

class TestReminderSend(BaseTest):
    def login_with(self, account):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        return login_page.do_successful_login_with(account)

    def go_to_reminder_page(self, project):
        global_navigation = self.login_with(TRIAL_CREDENTIALS_VALIDATES)
        all_project_page = global_navigation.navigate_to_view_all_project_page()
        overview_page = all_project_page.navigate_to_project_overview_page(project[PROJECT_NAME])
        return overview_page.navigate_to_reminder_page()

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

    @attr("functional_test")
    def test_trial_account_should_see_reminder_not_work_message_at_reminder_tab_in_active_project(self):
        all_reminder_pages = self.go_to_reminder_page(DISABLED_REMNIDER)
        self.assertEqual(DISABLED_REMNIDER[WARNING_MESSAGE], all_reminder_pages.get_warning_message())

    @attr("functional_test")
    def test_trial_account_should_see_reminder_not_work_message_at_sent_tab_in_active_project(self):
        all_reminder_pages = self.go_to_reminder_page(DISABLED_REMNIDER)
        all_reminder_pages.click_sent_reminder_tab()
        self.assertEqual(DISABLED_REMNIDER[WARNING_MESSAGE], all_reminder_pages.get_warning_message())


