from nose.plugins.attrib import attr
from datawinners.questionnaire.library import QuestionnaireLibrary
from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import by_css, random_string
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.dataextractionapitests.data_extraction_api_data import VALID_CREDENTIALS
from tests.questionnaireTemplateTests.questionnaire_template_test_data import SELECTED_TEMPLATE_NAME, NEW_PROJECT_DATA, SELECTED_TEMPLATE_QUESTIONS


@attr("functional_test")
class TestProjectCreationFromTemplate(HeadlessRunnerTest):
    def setUp(self):
        self.template_library = QuestionnaireLibrary()
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        self.global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)

    def test_should_create_project_from_template(self):
        dashboard_page = self.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        create_questionnaire_options_page.select_create_questionnaire_by_template_option()

        self.assertEqual(create_questionnaire_options_page.get_template_name(), SELECTED_TEMPLATE_NAME)
        self.assertListEqual(create_questionnaire_options_page.get_template_questions(), SELECTED_TEMPLATE_QUESTIONS)
        create_questionnaire_page = create_questionnaire_options_page.continue_to_questionnaire_page()
        create_questionnaire_page.type_project_name(NEW_PROJECT_DATA)
        self.assertEqual(create_questionnaire_page.get_existing_questions(), SELECTED_TEMPLATE_QUESTIONS)
        self.driver.find(by_css("#questionnaire-code")).send_keys(random_string(5))
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully()
        self.assertIsNotNone(project_overview_page.get_project_title())
        is_outgoing_sms_enabled = project_overview_page.navigate_send_message_tab().navigate_to_automatic_reply_sms_page().get_reply_messages_switch_status()
        self.assertTrue(is_outgoing_sms_enabled)
