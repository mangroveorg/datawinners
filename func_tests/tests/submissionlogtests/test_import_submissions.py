import os
import json

from django.test import Client

from framework.base_test import HeadlessRunnerTest
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from datawinners.tests.data import DEFAULT_TEST_USER, DEFAULT_TEST_PASSWORD
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.questionnaireTemplateTests.questionnaire_template_test_data import NEW_PROJECT_DATA, GEN_RANDOM, TYPE, QUESTIONS, QUESTION, QUESTIONNAIRE_CODE, WORD, LIMIT, LIMITED, MAX

DIR = os.path.dirname(__file__)

class TestImportSubmissions(HeadlessRunnerTest):


    QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS", GEN_RANDOM: True,
                          QUESTIONS: [{QUESTION: "Clinic admin name", TYPE: WORD, LIMIT: LIMITED,
                                       MAX: "100"}],
                          }

    def setUp(self):
        self.test_data = os.path.join(DIR, 'testdata')
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        self.client = Client()
        self.client.login(username=DEFAULT_TEST_USER, password=DEFAULT_TEST_PASSWORD)


    def test_should_import_and_upload_submission_only_on_behalf_of_logged_in_admin_or_associated_datasenders_to_the_questionnaire(self):

        logged_in_project_admin = 'rep276'
        associated_data_sender = 'rep4'
        disassociated_admin = 'rep11'

        global_navigation_page = GlobalNavigationPage(self.driver)
        dashboard_page = global_navigation_page.navigate_to_dashboard_page()
        create_optional_questionnaire_page = dashboard_page.navigate_to_create_project_page()
        questionnaire_tab_page = create_optional_questionnaire_page.select_blank_questionnaire_creation_option()
        questionnaire_tab_page.create_questionnaire_with(NEW_PROJECT_DATA, self.QUESTIONNAIRE_DATA)
        project_overview_page=questionnaire_tab_page.save_and_create_project_successfully()
        project_name = project_overview_page.get_project_title()

        all_data_sender_page = global_navigation_page.navigate_to_all_data_sender_page()
        all_data_sender_page.associate_datasender_to_projects(associated_data_sender, [project_name])
        all_questionnaire_page = global_navigation_page.navigate_to_view_all_project_page()
        project_overview_page = all_questionnaire_page.navigate_to_project_overview_page(project_name)
        project_data_senders_page = project_overview_page.navigate_to_datasenders_page()

        project_data_senders_page.select_a_data_sender_by_rep_id(logged_in_project_admin)
        project_data_senders_page.select_a_data_sender_by_rep_id(disassociated_admin)
        project_data_senders_page.disassociate_from_questionnaire()

        data_analysis_page = project_overview_page.navigate_to_data_page()
        data_analysis_page.navigate_to_all_data_record_page()

        project_form_code = project_overview_page.get_questionnaire_code()
        project_id = project_overview_page.get_project_id()
        res = self.client.post(path="/project/import-submissions/"+project_form_code+"?project_id="+project_id+"&qqfile=import.xls",
                               data=open(os.path.join(self.test_data, 'import.xls'), 'r').read(),
                               content_type='application/octet-stream')
        submission = json.loads(res.content)

        self.assertEquals(len(submission['success_submissions']), 2)
        self.assertEquals(len(submission['errored_submission_details']), 2)
        first_submission = submission['success_submissions'][0]
        third_submission = submission['success_submissions'][1]
        self.assertEquals(first_submission['dsid'], logged_in_project_admin)
        self.assertEquals(first_submission['user_dsid'], logged_in_project_admin)
        self.assertEquals(first_submission['q2'],'admin answers the question !!')
        self.assertEquals(third_submission['dsid'], associated_data_sender)
        self.assertEquals(third_submission['user_dsid'], logged_in_project_admin)
        self.assertEquals(third_submission['q2'],'on behalf of datasender')