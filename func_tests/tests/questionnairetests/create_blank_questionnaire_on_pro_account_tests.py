from nose.plugins.attrib import attr
from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import login
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from tests.projects.customizedreplysmstests.customized_reply_sms_data import PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA
from framework.utils.database_manager_postgres import DatabaseManager
from tests.logintests.login_data import *
from mangrove.form_model.form_model import get_form_model_by_code
from datawinners.project.models import Project
from datawinners.main.database import get_db_manager


class TestCreateBlankQuestionnaireProAccount(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        cls.organization = DatabaseManager().get_organization_by_email(fetch_(from_(USERNAME), VALID_CREDENTIALS))
        cls.organization.account_type = "Pro"
        cls.organization.save()
        HeadlessRunnerTest.setUpClass()
        cls.global_navigation = login(cls.driver)
        cls.dbm = get_db_manager('hni_testorg_slx364903')

    @classmethod
    def tearDownClass(cls):
        cls.organization.account_type = "Pro SMS"
        cls.organization.save()
        teardown_driver(cls.driver)

    @classmethod
    def _create_project_and_go_to_registered_datasenders(cls):
        dashboard_page = cls.global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()
        cls.create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        cls.create_questionnaire_page.create_questionnaire_with(PROJECT_DATA, PROJECT_QUESTIONNAIRE_DATA)
        questionnaire_code = cls.create_questionnaire_page.get_questionnaire_code()
        overview_page = cls.create_questionnaire_page.save_and_create_project_successfully()
        cls.project_name = overview_page.get_project_title()
        cls.questionnaire_code = questionnaire_code
        return overview_page.navigate_to_datasenders_page()

    @attr('functional_test')
    def test_should_not_show_change_setting_option(self):
        self.registered_datasenders_page = self._create_project_and_go_to_registered_datasenders()
        self.assertFalse(self.registered_datasenders_page.is_change_setting_option_displayed())
        form_model = get_form_model_by_code(self.dbm, self.questionnaire_code)
        project = Project.from_form_model(form_model)
        self.assertFalse(project.is_open_survey)


  