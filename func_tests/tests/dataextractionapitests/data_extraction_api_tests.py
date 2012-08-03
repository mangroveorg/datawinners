from urllib2 import urlopen
from simplejson.decoder import JSONDecoder
from framework.base_test import BaseTest
from framework.utils.common_utils import generateId
from framework.utils.data_fetcher import fetch_, from_
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ALL_SUBJECT, DATA_WINNER_ADD_SUBJECT, DATA_WINNER_DASHBOARD_PAGE, url, DATA_WINNER_HOST, DATA_WINNER_PORT
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
        return JSONDecoder.decode(http_response.read())

    def test_get_data_by_subject_type_and_subject_id(self):
        self.prepare_submission_data()
        result = self.get_data_by_uri("/api/get_for_subject/%s/%s" % (self.subject_type, self.subject_id))
        self.assertTrue(isinstance(result, list))
