import unittest
from django.utils.unittest.case import SkipTest

from nose.plugins.attrib import attr

from framework.base_test import setup_driver, teardown_driver
from datawinners.messageprovider.tests.test_message_handler import THANKS
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_USER_ACTIVITY_LOG_PAGE, LOGOUT
from tests.addusertests.add_user_data import ADD_USER_DATA
from tests.logintests.login_data import VALID_CREDENTIALS, USERNAME, PASSWORD
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.alluserspage.all_users_page import AllUsersPage
from tests.alluserstests.all_users_data import *
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from tests.projects.questionnairetests.project_questionnaire_data import SENDER, RECEIVER, SMS, VALID_SUMMARY_REPORT_DATA
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.activitylogpage.show_activity_log_page import ShowActivityLogPage


@attr('suit_1')
class TestAllUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()

    def setUp(self):
        self.global_navigation = GlobalNavigationPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    def prerequisites_for_all_users(self):
        self.login()
        self.driver.go_to(ALL_USERS_URL)
        return AllUsersPage(self.driver)

    def login(self, credential=VALID_CREDENTIALS):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(credential)

    @attr('functional_test')
    def test_should_not_show_delete_if_any_users_selected(self):
        all_users_page = self.prerequisites_for_all_users()
        all_users_page.click_check_all_users(check=False)
        all_users_page.click_action_button()
        self.assertFalse(all_users_page.actions_menu_shown())

    @attr('functional_test')
    def test_should_not_delete_super_admin_user(self):
        all_users_page = self.prerequisites_for_all_users()
        all_users_page.click_check_all_users()
        all_users_page.select_delete_action(confirm=True)
        message = all_users_page.get_message()
        self.assertEqual(message, ADMIN_CANT_BE_DELETED)

    @attr('functional_test')
    @SkipTest
    def test_should_create_activity_log_and_submit_data(self):
        all_users_page = self.prerequisites_for_all_users()
        add_user_page = all_users_page.navigate_to_add_user()
        add_user_page.add_user_with(NEW_USER_DATA)
        self.driver.go_to(LOGOUT)
        new_user_credential = {USERNAME: NEW_USER_DATA[USERNAME], PASSWORD: "test123"}
        self.login(credential=new_user_credential)
        self.driver.go_to(ALL_USERS_URL)
        all_users_page =  AllUsersPage(self.driver)
        add_user_page = all_users_page.navigate_to_add_user()
        add_user_page.add_user_with(ADD_USER_DATA)
        self.driver.go_to(url("/project/"))
        project_name, questionnaire_code = self.create_project()
        self.send_submission(questionnaire_code)
        self.delete_user(NEW_USER_DATA[USERNAME])
        self.check_sent_submission(project_name)
        self.check_deleted_user_name_on_activity_log_page(project_name)

    def send_submission(self, questionnaire_code):
        self.driver.execute_script("window.open('%s')" % DATA_WINNER_SMS_TESTER_PAGE)
        new_tab = self.driver.window_handles[1]
        first_tab = self.driver.window_handles[0]
        self.driver.switch_to_window(new_tab)
        sms_tester_page = SMSTesterPage(self.driver)
        valid_sms = {SENDER: NEW_USER_DATA[MOBILE_PHONE],
                     RECEIVER: '919880734937',
                     SMS: "%s 10.10.2010" % questionnaire_code}
        sms_tester_page.send_sms_with(valid_sms)
        response = sms_tester_page.get_response_message()
        self.assertIn("Thank you", response)
        # self.assertRegexpMatches(response, THANKS % "Mamy")
        self.driver.close()
        self.driver.switch_to_window(first_tab)

    def create_project(self):
        dashboard_page = DashboardPage(self.driver)
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(VALID_SUMMARY_REPORT_DATA)
        create_project_page.continue_create_project()
        create_project_page.save_and_create_project()
        overview_page = ProjectOverviewPage(self.driver)
        questionnaire_code = overview_page.get_questionnaire_code()
        project_name = overview_page.get_project_title()
        return project_name, questionnaire_code

    def delete_user(self):
        self.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(self.driver)
        all_users_page.check_nth_user(2)
        all_users_page.select_delete_action(confirm=True)
        message = all_users_page.get_message()
        self.assertEqual(message, SUCCESSFULLY_DELETED_USER_MSG)

    def check_sent_submission(self, project_name):
        all_data_page = self.global_navigation.navigate_to_all_data_page()
        data_analysis_page = all_data_page.navigate_to_data_analysis_page(project_name)
        data_sender_name = data_analysis_page.get_all_data_records_by_column(2)
        self.assertTrue("kimi" in data_sender_name[0])

    def check_deleted_user_name_on_activity_log_page(self, project_name):
        self.driver.go_to(DATA_WINNER_USER_ACTIVITY_LOG_PAGE)
        activity_log_page = ShowActivityLogPage(self.driver)
        username = activity_log_page.get_data_on_cell(1, 1)
        action = activity_log_page.get_data_on_cell(1, 2)
        project_name_on_log_page = activity_log_page.get_data_on_cell(2, 4)
        self.assertEqual(project_name_on_log_page, project_name)
        self.assertTrue("Deleted User" in username, username)
