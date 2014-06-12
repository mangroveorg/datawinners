from nose.plugins.attrib import attr
from tests.testsettings import UI_TEST_TIMEOUT
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_xpath, by_css

from pages.loginpage.login_page import login
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_USER_ACTIVITY_LOG_PAGE, LOGOUT
from tests.logintests.login_data import VALID_CREDENTIALS, PASSWORD
from pages.alluserspage.all_users_page import AllUsersPage
from tests.alluserstests.all_users_data import *
from pages.dashboardpage.dashboard_page import DashboardPage
from tests.projects.questionnairetests.project_questionnaire_data import SENDER, RECEIVER, SMS, VALID_SUMMARY_REPORT_DATA, QUESTIONNAIRE_CODE, \
    DEFAULT_QUESTION, QUESTION, GEN_RANDOM, CODE, TYPE, DATE, QUESTIONS, DATE_FORMAT, DD_MM_YYYY
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.activitylogpage.show_activity_log_page import ShowActivityLogPage


QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "addtest", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "q1"},
                      QUESTIONS: [{QUESTION: u"Date of report in DD.MM.YYY format", CODE: u"q3", TYPE: DATE,
                                   DATE_FORMAT: DD_MM_YYYY}]}

class TestAllUsers(HeadlessRunnerTest):

    def setUp(self):
        self.global_navigation = login(self.driver, VALID_CREDENTIALS)
        self.driver.go_to(ALL_USERS_URL)
        self.all_users_page = AllUsersPage(self.driver)

    def tearDown(self):
        self.global_navigation.sign_out()

    @attr('functional_test')
    def test_should_not_show_delete_if_any_users_selected(self):
        self.all_users_page.click_check_all_users(check=False)
        self.all_users_page.click_action_button()
        self.assertFalse(self.all_users_page.actions_menu_shown())

    @attr('functional_test')
    def test_should_not_delete_super_admin_user(self):
        self.all_users_page.click_check_all_users()
        self.all_users_page.select_delete_action(confirm=True)
        message = self.all_users_page.get_message()
        self.assertEqual(message, ADMIN_CANT_BE_DELETED)

    @attr('functional_test')
    def test_should_create_activity_log_and_submit_data(self):
        add_user_page = self.all_users_page.navigate_to_add_user()
        add_user_page.add_user_with(NEW_USER_DATA)
        self.driver.go_to(LOGOUT)
        new_user_credential = {USERNAME: NEW_USER_DATA[USERNAME], PASSWORD: "test123"}
        login(self.driver, new_user_credential)
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
        self.driver.create_screenshot("sms_error.png")
        self.assertIn("Thank you", response)
        # self.assertRegexpMatches(response, THANKS % "Mamy")
        self.driver.close()
        self.driver.switch_to_window(first_tab)

    def create_project(self):
        dashboard_page = DashboardPage(self.driver)
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page = create_project_page.select_blank_questionnaire_creation_option()
        create_project_page.create_questionnaire_with(VALID_SUMMARY_REPORT_DATA, QUESTIONNAIRE_DATA)
        overview_page = create_project_page.save_and_create_project_successfully()
        questionnaire_code = overview_page.get_questionnaire_code()
        project_name = overview_page.get_project_title()
        return project_name, questionnaire_code

    def delete_user(self, username):
        self.driver.go_to(LOGOUT)
        login(self.driver, VALID_CREDENTIALS)
        self.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(self.driver)
        self.driver.find(by_xpath("//td[contains(.,'%s')]/../td/input" % username)).click()
        all_users_page.select_delete_action(confirm=True)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css("span.loading"), True)
        self.driver.wait_until_modal_dismissed()
        message = all_users_page.get_message()
        self.assertEqual(message, SUCCESSFULLY_DELETED_USER_MSG)

    def check_sent_submission(self, project_name):
        all_data_page = self.global_navigation.navigate_to_all_data_page()
        data_analysis_page = all_data_page.navigate_to_data_analysis_page(project_name)
        data_sender_name = data_analysis_page.get_all_data_on_nth_row(1)[1]
        self.assertTrue("kimi" in data_sender_name)

    def check_deleted_user_name_on_activity_log_page(self, project_name):
        self.driver.go_to(DATA_WINNER_USER_ACTIVITY_LOG_PAGE)
        username = self.driver.find(by_xpath("//td[contains(.,'%s')]/../td[1]" % project_name)).text
        action = self.driver.find(by_xpath("//td[contains(.,'%s')]/../td[2]" % project_name)).text
        self.assertEqual("Deleted User", username)
        self.assertEqual("Created Project", action)
