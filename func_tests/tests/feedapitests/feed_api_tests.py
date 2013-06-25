from datetime import datetime
import unittest
import urllib2
import jsonpickle
from nose.plugins.attrib import attr
import requests
from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_LOGIN_PAGE
from tests.createquestionnairetests.create_questionnaire_data import QUESTIONNAIRE_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.smstestertests.sms_tester_data import *
from tests.submissionlogtests.edit_survey_response_data import get_sms_data_with_questionnaire_code
from tests.createprojecttests.create_project_data import CREATE_NEW_PROJECT_DATA

DATE_FORMAT = '%d-%m-%Y %H:%M:%S'


class TestFeeds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls._login()
        cls._create_project()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def _login(cls):
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        cls.navigation_page = LoginPage(cls.driver).do_successful_login_with(VALID_CREDENTIALS)

    @classmethod
    def _create_project(cls):
        cls.dashboard_page = DashboardPage(cls.driver)
        create_project_page = cls.dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(CREATE_NEW_PROJECT_DATA)
        create_project_page.continue_create_project()
        CreateQuestionnairePage(cls.driver).create_questionnaire_with(QUESTIONNAIRE_DATA)
        create_project_page.save_and_create_project_successfully()

    def _submit_data(self):
        project_name, questionnaire_code = self._get_project_details()
        self._submit_sms_data(get_sms_data_with_questionnaire_code(questionnaire_code))
        return project_name, questionnaire_code

    @attr('functional_test')
    def test_should_get_feeds(self):
        start_date = datetime.utcnow()
        start_date = urllib2.quote(start_date.strftime(DATE_FORMAT).encode("utf-8"))
        project_name, questionnaire_code = self._submit_data()
        end_date = datetime.utcnow()
        end_date = urllib2.quote(end_date.strftime(DATE_FORMAT).encode("utf-8"))
        url = "http://localhost:8000/feeds/" + questionnaire_code + "?start_date=" + start_date + "&end_date=" + end_date
        actual_data = requests.get(url, auth=('tester150411@gmail.com', 'tester150411' ))
        response_list = jsonpickle.decode(actual_data.content)
        self.assertEquals(1, len(response_list))
        feed_entry = response_list[0]
        expected_data = {'q1': 'wp01', 'q3': '5', 'q2': '25.12.2010', 'q5': ['a'], 'q4': '24.12.2010', 'q7': ['c'],
                         'q6': 'admin', 'q8': '12,12'}
        self.assertEquals(feed_entry['values'], expected_data)
        self.assertEquals('rep8', feed_entry['data_sender_id'])
        self.assertEquals(feed_entry['status'], 'success')
        self.assertRegexpMatches(feed_entry['feed_modified_time'],
                                 '\d{4}-\d{2}-\d{2}\W\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}\:\d{2}')
        self.assertRegexpMatches(feed_entry['submission_modified_time'],
                                 '\d{4}-\d{2}-\d{2}\W\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}\:\d{2}')


    def _get_project_details(self):
        overview_page = ProjectOverviewPage(self.driver)
        return overview_page.get_project_title(), overview_page.get_questionnaire_code()

    def _submit_sms_data(self, sms_data):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        page = SMSTesterPage(self.driver)
        page.send_sms_with(sms_data)
        self.assertEqual(page.get_response_message(), fetch_(MESSAGE, from_(sms_data)))

