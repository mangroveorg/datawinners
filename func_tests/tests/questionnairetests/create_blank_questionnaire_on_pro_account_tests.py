from nose.plugins.attrib import attr
from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import login
from pages.projectspage.projects_page import ProjectsPage
from pages.questionnairetabpage.questionnaire_tab_page import MANDATORY_FIELD_ERROR_MESSAGE
from pages.warningdialog.questionnaire_modified_dialog import QuestionnaireModifiedDialog
from tests.projects.questionnairetests.project_questionnaire_data import QUESTIONS_WITH_INVALID_ANSWER_DETAILS, WATERPOINT_QUESTIONNAIRE_DATA, QUESTIONS, DIALOG_PROJECT_DATA, NEW_UNIQUE_ID_TYPE
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from tests.projects.customizedreplysmstests.customized_reply_sms_data import PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA
from framework.utils.database_manager_postgres import DatabaseManager


class TestCreateBlankQuestionnaireProAccount(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        cls.organization = DatabaseManager().get_organization_by_email(VALID_CREDENTIALS.get(USERNAME))
        cls.organization.account_type = "Pro"
        cls.organization.save()
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        dashboard_page = cls.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()

    @classmethod
    def tearDownClass(cls):
        cls.organization.account_type = "Pro SMS"
        cls.organization.save()
        teardown_driver(cls.driver)

    @classmethod
    def _create_project_and_go_to_registered_datasenders(cls):
        global_navigation = GlobalNavigationPage(cls.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()
        cls.project_name = overview_page.get_project_title()
        cls.questionnaire_code = questionnaire_code
        return overview_page.navigate_to_datasenders_page()

    @attr('functional_test')
    def test_should_clear_questionnaire_form_on_recreating_questionnaire(self):
        self.registered_datasenders_page = self._create_project_and_go_to_registered_datasenders()
        
        create_questionnaire_page.set_questionnaire_title("Some title")
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.change_question_type(WATERPOINT_QUESTIONNAIRE_DATA[QUESTIONS][0])
        create_questionnaire_page.click_add_question_link()
        create_questionnaire_page.change_question_type(QUESTIONS_WITH_INVALID_ANSWER_DETAILS[0])
        create_questionnaire_page.submit_errored_questionnaire()
        create_questionnaire_page.back_to_questionnaire_creation_page().select_blank_questionnaire_creation_option()
        self.assertEqual(create_questionnaire_page.get_questionnaire_title(), "")#, "Questionnaire title should be blank")
        self.assertEqual(create_questionnaire_page.get_existing_questions_count(), 0,
                         "No questions should be present for a blank questionnaire")
        self.assertTrue(create_questionnaire_page.get_select_or_edit_question_message().is_displayed(),
                        "No question should be selected by default")

    

  