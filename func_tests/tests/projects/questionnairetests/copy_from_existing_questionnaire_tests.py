from time import sleep
from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login, LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from tests.projects.questionnairetests.project_questionnaire_data import COPY_PROJECT_QUESTIONNAIRE_DATA, COPY_PROJECT_DATA
from tests.testsettings import UI_TEST_TIMEOUT
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, LOGOUT
from tests.dashboardtests.dashboard_tests_data import USER_RASITEFA_CREDENTIALS


class TestCopyExistingQuestionnaire(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)

    @attr("functional_test")
    def test_to_copy_existing_questionnaire(self):
        self.project_name, self.questionnaire_code = self._create_project(COPY_PROJECT_DATA, COPY_PROJECT_QUESTIONNAIRE_DATA)
        create_questionnaire_options_page = self.global_navigation.navigate_to_dashboard_page()\
                                                .navigate_to_create_project_page()
        actual_questions = create_questionnaire_options_page.get_questions_list_for_selected_project(self.project_name)
        self.assertListEqual(["Some dummy question"], actual_questions, "Questions should match existing questions on questionnaire tab")
        create_questionnaire_page = create_questionnaire_options_page.continue_to_questionnaire_page()
        self.assertListEqual(["Some dummy question"], create_questionnaire_page.get_existing_questions())
        new_project_title = create_questionnaire_page.set_questionnaire_title("Copied Project", generate_random=True)
        copied_projects_reminder_page = create_questionnaire_page.save_and_create_project_successfully(click_ok=False)\
            .navigate_to_reminder_page()
        self.assertEqual("week", copied_projects_reminder_page.get_frequency())
        self.assertEqual("5", copied_projects_reminder_page.get_week_day())

        is_outgoing_sms_enabled = copied_projects_reminder_page.navigate_to_automatic_reply_sms_page()\
                                  .get_reply_messages_switch_status()
        self.assertFalse(is_outgoing_sms_enabled)

        self.global_navigation.navigate_to_view_all_project_page().navigate_to_create_project_page()
        self.assertIn(new_project_title, create_questionnaire_options_page.get_project_list())

    @classmethod
    def _create_project(cls, project_data, questionnaire_data):
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(project_data, questionnaire_data)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()

        reminder_setting_page = ProjectOverviewPage(cls.driver).navigate_to_reminder_page()
        reminder_setting_page.set_frequency("Week")
        reminder_setting_page.set_week_day("Friday")
        reminder_setting_page.enable_before_deadline_reminder()
        reminder_setting_page.save_reminders()
        cls.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.success-message-box'),want_visible=True)
        automatic_reply_sms_page = reminder_setting_page.navigate_to_automatic_reply_sms_page()
        automatic_reply_sms_page.turn_off_reply_messages()
        cls.questionnaire_tab_page = overview_page.navigate_to_questionnaire_tab()
        cls.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, 'Questionnaire')
        return overview_page.get_project_title(), questionnaire_code

    @attr('functional_test')
    def test_should_check_all_questionnaires_are_available_for_copy_when_creating_questionnaire(self):
        questionnaire_count_for_ngo_admin = self._get_number_of_available_questionnaire()
        self.assertNotEqual(0, questionnaire_count_for_ngo_admin)
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(USER_RASITEFA_CREDENTIALS)
        questionnaire_count_for_simple_user = self._get_number_of_available_questionnaire()
        self.assertNotEqual(0, questionnaire_count_for_simple_user)
        self.assertEqual(questionnaire_count_for_simple_user, questionnaire_count_for_ngo_admin)
        
    def _get_number_of_available_questionnaire(self):
        create_questionnaire_options_page = self.global_navigation.navigate_to_dashboard_page()\
                                                .navigate_to_create_project_page()
        return create_questionnaire_options_page.count_questionnaires_available_for_copy()
