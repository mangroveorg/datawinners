import json
from urllib2 import urlopen
from nose.plugins.attrib import attr
from framework.base_test import BaseTest, setup_driver, teardown_driver
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
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.prepare_submission_data()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def login(cls):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    @classmethod
    def prepare_subject_type(cls):
        cls.driver.go_to(DATA_WINNER_ALL_SUBJECT)
        add_subject_type_page = AddSubjectTypePage(cls.driver)
        add_subject_type_page.click_on_accordian_link()
        cls.subject_type = SUBJECT_TYPE + generateId()
        cls.subject_type = cls.subject_type.strip()
        add_subject_type_page.add_entity_type_with(cls.subject_type)

    @classmethod
    def prepare_subject(cls):
        cls.driver.go_to(DATA_WINNER_ADD_SUBJECT + cls.subject_type)
        add_subject_page = AddSubjectPage(cls.driver)
        add_subject_page.add_subject_with(VALID_DATA)
        add_subject_page.submit_subject()
        flash_message = add_subject_page.get_flash_message()
        cls.subject_id = flash_message[flash_message.find(":") + 1:].strip()

    @classmethod
    def create_project(cls):
        cls.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        dashboard_page = DashboardPage(cls.driver)

        create_project_page = dashboard_page.navigate_to_create_project_page()
        VALID_PROJECT_DATA[SUBJECT] = cls.subject_type
        create_project_page.create_project_with(VALID_PROJECT_DATA)
        create_project_page.continue_create_project()
        create_questionnaire_page = CreateQuestionnairePage(cls.driver)
        create_questionnaire_page.add_question(QUESTION)
        create_questionnaire_page.save_and_create_project_successfully()
        cls.driver.wait_for_page_with_title(15, fetch_(PAGE_TITLE, from_(VALID_PROJECT_DATA)))

    @classmethod
    def activate_project(cls):
        overview_page = ProjectOverviewPage(cls.driver)
        activate_project_light_box = overview_page.open_activate_project_light_box()
        activate_project_light_box.activate_project()

    @classmethod
    def submit_data(cls):
        overview_page = ProjectOverviewPage(cls.driver)
        data_page = overview_page.navigate_to_data_page()
        web_submission_tab = data_page.navigate_to_web_submission_tab()
        [web_submission_tab.fill_and_submit_answer(answer) for answer in VALID_ANSWERS]

    @classmethod
    def prepare_submission_data(cls):
        cls.login()
        cls.prepare_subject_type()
        cls.prepare_subject()
        cls.create_project()
        cls.activate_project()
        cls.submit_data()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_data_by_uri(self, uri):
        http_response = urlopen(url(uri))

        return json.loads(http_response.read())

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_subject_id(self):
        result = self.get_data_by_uri(
            "/api/get_for_subject/%s/%s/" % (self.__class__.subject_type, self.__class__.subject_id))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 5)
        self.assertEqual(result["message"], "You can access the data in value field.")
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_subject_id_and_same_date(self):
        result = self.get_data_by_uri(
            "/api/get_for_subject/%s/%s/%s/%s" % (
                self.__class__.subject_type, self.__class__.subject_id, "03-08-2012", "03-08-2012"))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 1)
        self.assertEqual(result["message"], "You can access the data in value field.")
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_subject_id_and_different_date(self):
        result = self.get_data_by_uri(
            "/api/get_for_subject/%s/%s/%s/%s" % (
                self.__class__.subject_type, self.__class__.subject_id, "03-08-2012", "06-08-2012"))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 4)
        self.assertEqual(result["message"], "You can access the data in value field.")
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_subject_id_and_start_date(self):
        result = self.get_data_by_uri(
            "/api/get_for_subject/%s/%s/%s" % (
                self.__class__.subject_type, self.__class__.subject_id, "03-08-2012"))
        value = result['value']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertTrue(len(value), 4)
        self.assertEqual(result["message"], "You can access the data in value field.")
        self.assertEqual(value[0][QUESTION[QUESTION_NAME]], VALID_ANSWERS[0][1][ANSWER])

    @attr('functional_test')
    def test_get_data_for_subject_with_not_exist_subject_type(self):
        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/" % ("not_exist", "001"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Entity type [not_exist] is not defined.")

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_not_exist_subject_id(self):
        result = self.get_data_by_uri("/api/get_for_subject/%s/%s/" % (self.__class__.subject_type, "not_exist"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Entity [not_exist] is not registered.")

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_subject_id_and_wrong_date_format(self):
        result = self.get_data_by_uri(
            "/api/get_for_subject/%s/%s/%s/%s" % (
                self.__class__.subject_type, self.__class__.subject_id, "03082012", "06082012"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "The format of start and end date should be DD-MM-YYYY. Example: 25-12-2011")

    @attr('functional_test')
    def test_get_data_for_subject_with_subject_type_and_subject_id_and_wrong_date(self):
        result = self.get_data_by_uri(
            "/api/get_for_subject/%s/%s/%s/%s" % (
                self.__class__.subject_type, self.__class__.subject_id, "06-08-2012", "03-08-2012"))
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Start date must before end date.")