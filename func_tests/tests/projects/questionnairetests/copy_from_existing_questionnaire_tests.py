from nose.plugins.attrib import attr

from framework.base_test import HeadlessRunnerTest
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from tests.projects.questionnairetests.project_questionnaire_data import COPY_PROJECT_QUESTIONNAIRE_DATA, COPY_PROJECT_DATA


class TestCopyExistingQuestionnaire(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        cls.project_name, cls.questionnaire_code = cls._create_project(COPY_PROJECT_DATA, COPY_PROJECT_QUESTIONNAIRE_DATA)

    @attr("functional_test")
    def test_to_copy_existing_questionnaire1(self):
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
        self.assertEqual("Same", copied_projects_reminder_page.get_deadline_type_for_week())

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
        reminder_setting_page.set_deadline_type_for_week("Same week")
        reminder_setting_page.set_week_day("Friday")
        reminder_setting_page.enable_before_deadline_reminder()
        reminder_setting_page.save_reminders()

        reminder_setting_page.navigate_to_automatic_reply_sms_page().turn_off_reply_messages()

        cls.questionnaire_tab_page = overview_page.navigate_to_questionnaire_tab()
        return overview_page.get_project_title(), questionnaire_code

