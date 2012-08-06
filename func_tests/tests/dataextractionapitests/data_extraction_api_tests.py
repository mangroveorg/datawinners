import json
from urllib2 import urlopen
from framework.base_test import BaseTest
from framework.utils.common_utils import generateId
from framework.utils.data_fetcher import fetch_, from_
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ALL_SUBJECT, DATA_WINNER_ADD_SUBJECT, DATA_WINNER_DASHBOARD_PAGE, url
from tests.dataextractionapitests.data_extraction_api_data import *


class DataExtractionAPITestCase(BaseTest):
    def login(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    def prepare_subject_type(self):
        self.driver.go_to(DATA_WINNER_ALL_SUBJECT)
        add_subject_type_page = AddSubjectTypePage(self.driver)
        add_subject_type_page.click_on_accordian_link()
        self.subject_type = SUBJECT_TYPE + generateId()
        self.subject_type = self.subject_type.strip()
        add_subject_type_page.add_entity_type_with(self.subject_type)

    def prepare_subject(self):
        self.driver.go_to(DATA_WINNER_ADD_SUBJECT + self.subject_type)
        add_subject_page = AddSubjectPage(self.driver)
        add_subject_page.add_subject_with(VALID_DATA)
        add_subject_page.submit_subject()
        flash_message = add_subject_page.get_flash_message()
        self.subject_id = flash_message[flash_message.find(":") + 1:].strip()

    def create_project(self):
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        dashboard_page = DashboardPage(self.driver)

        create_project_page = dashboard_page.navigate_to_create_project_page()
        VALID_PROJECT_DATA[SUBJECT] = self.subject_type
        create_project_page.create_project_with(VALID_PROJECT_DATA)
        create_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(self.driver)
        create_questionnaire_page.add_question(QUESTION)
        create_questionnaire_page.save_and_create_project_successfully()
        self.driver.wait_for_page_with_title(15, fetch_(PAGE_TITLE, from_(VALID_PROJECT_DATA)))
        self.assertEqual(self.driver.get_title(),
            fetch_(PAGE_TITLE, from_(VALID_PROJECT_DATA)))

    def activate_project(self):
        overview_page = ProjectOverviewPage(self.driver)
        activate_project_light_box = overview_page.open_activate_project_light_box()
        activate_project_light_box.activate_project()

    def submit_data(self):
        overview_page = ProjectOverviewPage(self.driver)
        data_page = overview_page.navigate_to_data_page()
        web_submission_tab = data_page.navigate_to_web_submission_tab()
        [web_submission_tab.fill_and_submit_answer(answer) for answer in VALID_ANSWERS]

    def prepare_submission_data(self):
        self.login()
        self.prepare_subject_type()
        self.prepare_subject()
        self.create_project()
        self.activate_project()
        self.submit_data()

    def get_data_by_uri(self, uri):
        http_response = urlopen(url(uri))

        return json.loads(http_response.read())

    def test_get_data_for_subject(self):
        self.prepare_submission_data()
        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/" % (self.subject_type, self.subject_id))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 5)
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/%s/%s" % (self.subject_type, self.subject_id, "03-08-2012", "03-08-2012"))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 1)
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/%s/%s" % (self.subject_type, self.subject_id, "03-08-2012", "06-08-2012"))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 4)
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/" % ("not_exist", "001"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Entity type [not_exist] is not defined.")

        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/" % (self.subject_type, "not_exist"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Entity [not_exist] is not registered.")

        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/%s/%s" % (self.subject_type, self.subject_id, "03082012", "06082012"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "The format of start and end date should be DD-MM-YYYY.")

        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/%s/%s" % (self.subject_type, self.subject_id, "06-08-2012", "03-08-2012"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Start date must before end date.")


