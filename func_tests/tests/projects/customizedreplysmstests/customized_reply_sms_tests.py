from nose.plugins.attrib import attr
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import random_string
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import login
from tests.projects.customizedreplysmstests.customized_reply_sms_data import PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA


class TestCustomizedReplySms(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        cls.automatic_reply_sms_page = cls._create_project_and_go_to_automatic_reply_sms_page(PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA)

    @classmethod
    def _create_project_and_go_to_automatic_reply_sms_page(cls, project_data, questionnaire_data):
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(project_data, questionnaire_data)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()
        cls.project_name = overview_page.get_project_title()
        cls.questionnaire_code = questionnaire_code
        broadcast_message_page = overview_page.navigate_send_message_tab()
        return broadcast_message_page.navigate_to_automatic_reply_sms_page()

    def test_project_reply_sms_language(self):
        languages_page = self.automatic_reply_sms_page.choose_automatic_reply_language('new')
        new_language = 'language' + random_string(4)
        languages_page.add_new_language(new_language)
        self.assertEqual(languages_page.get_success_message(), 'Language Added succesfully')


