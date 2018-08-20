from datetime import datetime
import json
from time import sleep
import unittest

from nose.plugins.attrib import attr
import requests
from requests.auth import HTTPDigestAuth

from framework.base_test import HeadlessRunnerTest
from framework.utils.common_utils import generateId, skipUntil
from framework.utils.data_fetcher import fetch_, from_
from pages.allsubjectspage.add_subject_page import AddSubjectPage
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import login
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from testdata.test_data import DATA_WINNER_ALL_SUBJECT, DATA_WINNER_ADD_SUBJECT, DATA_WINNER_DASHBOARD_PAGE, url
from tests.dataextractionapitests.data_extraction_api_data import *
from mock import Mock
from datawinners.accountmanagement.models import Organization
from datawinners.submission.models import DatawinnerLog


class DataExtractionAPITestCase(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.DIGEST_CREDENTIALS = HTTPDigestAuth('tester150411@gmail.com', 'tester150411')
        cls.prepare_submission_data()

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
        cls.driver.go_to(DATA_WINNER_ADD_SUBJECT + cls.subject_type + "?web_view=True")
        add_subject_page = AddSubjectPage(cls.driver)
        add_subject_page.add_subject_with(VALID_DATA)
        add_subject_page.submit_subject()
        flash_message = add_subject_page.get_flash_message()
        cls.subject_id = flash_message[flash_message.find(":") + 1:].strip()

    @classmethod
    def create_project(cls):
        cls.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        dashboard_page = DashboardPage(cls.driver)

        questionnaire_creation_options_page = dashboard_page.navigate_to_create_project_page()
        # VALID_PROJECT_DATA[SUBJECT] = cls.subject_type
        create_questionnaire_page = questionnaire_creation_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(VALID_PROJECT_DATA, QUESTIONNAIRE_DATA)
        cls.form_code = create_questionnaire_page.get_questionnaire_code()
        create_questionnaire_page.save_and_create_project_successfully()
        cls.driver.wait_for_page_with_title(15, fetch_(PAGE_TITLE, from_(VALID_PROJECT_DATA)))


    @classmethod
    def submit_data(cls):
        overview_page = ProjectOverviewPage(cls.driver)
        data_page = overview_page.navigate_to_data_page()
        web_submission_tab = data_page.navigate_to_web_submission_tab()
        [web_submission_tab.fill_and_submit_answer(answer) for answer in VALID_ANSWERS]

    @classmethod
    def prepare_submission_data(cls):
        login(cls.driver, VALID_CREDENTIALS)
        cls.prepare_subject_type()
        cls.prepare_subject()
        cls.create_project()
        cls.submit_data()

    def get_data_by_uri(self, uri):
        http_response = requests.get(url(uri), auth=self.DIGEST_CREDENTIALS)
        return json.loads(http_response.content)


    @attr('functional_test')
    def test_get_data_for_form_with_form_code(self):
        sleep(2)
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/" % self.form_code)
        submissions = result['submissions']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 4)
        self.assertEqual(result["message"], SUCCESS_MESSAGE)
        self.assertEqual(submissions[0]["submission_data"]["q2"], VALID_ANSWERS[0][0][ANSWER])

    @attr('functional_test')
    def test_get_data_for_form_with_form_code_and_same_date(self):
        dt = datetime.now().strftime("%d-%m-%Y")
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/%s/%s/" % (self.form_code, dt, dt))
        submissions = result['submissions']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 4)
        self.assertEqual(result["message"], SUCCESS_MESSAGE)
        self.assertEqual(submissions[0]["submission_data"]["q2"], VALID_ANSWERS[0][0][ANSWER])

    @attr('functional_test')
    def test_get_data_for_form_with_form_code_and_only_start_date(self):
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/%s/" % (self.__class__.form_code, '03-08-2012'))
        submissions = result['submissions']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 4)
        self.assertEqual(result["message"], SUCCESS_MESSAGE)
        self.assertEqual(submissions[0]["submission_data"]["q2"], VALID_ANSWERS[0][0][ANSWER])

    @attr('functional_test')
    def test_get_data_for_form_with_form_code_with_success_status_set_to_false_when_pass_not_exist_form_code(self):
        unknow_form_code = "unknow_form_code"
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/" % unknow_form_code)
        submissions = result['submissions']
        self.assertFalse(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 0)
        self.assertEqual(result["message"], DOES_NOT_EXISTED_FORM_ERROR_MESSAGE_PATTERN % unknow_form_code)

    @attr('functional_test')
    def test_get_data_for_form_with_form_code_with_success_status_set_to_false_when_pass_wrong_date_format(self):
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/%s/%s/" % (self.__class__.form_code, "03082012", "06082012"))
        submissions = result['submissions']
        self.assertFalse(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 0)
        self.assertEqual(result["message"], DATA_FORMAT_ERROR_MESSAGE)

    @attr('functional_test')
    def test_get_data_for_form_with_form_code_with_success_status_set_to_false_when_end_date_before_start_date(self):
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/%s/%s/" % (self.__class__.form_code, '09-08-2012', '03-08-2012'))
        submissions = result['submissions']
        self.assertFalse(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 0)
        self.assertEqual(result["message"], DATE_WRONG_ORDER_ERROR_MESSAGE)

    @attr('functional_test')
    def test_get_data_for_form_with_form_code_without_data_return(self):
        result = self.get_data_by_uri(
            "/api/get_for_form/%s/%s/%s/" % (self.__class__.form_code, '03-08-2011', '03-08-2011'))
        submissions = result['submissions']
        self.assertTrue(result['success'])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(submissions), 0)
        self.assertEqual(result["message"], NO_DATA_SUCCESS_MESSAGE_FOR_QUESTIONNAIRE)


class TestUniqueIdExtraction(unittest.TestCase):
    def setUp(self):
        self.DIGEST_CREDENTIALS = HTTPDigestAuth('tester150411@gmail.com', 'tester150411')

    @attr('functional_test')
    def test_should_return_unique_ids_for_given_form_code(self):
        response = requests.get(url('/api/unique-id/wat/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 200)
        response_body = json.loads(response.content)
        unique_ids_ = response_body['unique-ids']
        self.assertEqual(len(unique_ids_), 3)
        self.assertIn({u'geo_code': u'23.0395677, 72.566005', u'name': u'Test',
                                              u'firstname': u'Ahmedabad waterpoint', u'short_code': u'wp01',
                                              u'deleted': False, u'location': u'India,Gujrat,Ahmedabad',
                                              u'mobile_number': u'1234563'}, unique_ids_)

        self.assertIn({u'geo_code': u'28.46385, 77.017838', u'name': u'Test',
                                              u'firstname': u'Gurgaon waterpoint', u'short_code': u'wp03',
                                              u'deleted': False, u'location': u'India,Haryana,Gurgaon',
                                              u'mobile_number': u'1234564'}, unique_ids_)

        self.assertIn({u'geo_code': u'23.251671, 69.66256', u'name': u'Test', u'firstname': u'Bhuj waterpoint',
                              u'short_code': u'wp02', u'deleted': False, u'location': u'India,Gujrat,Bhuj',
                              u'mobile_number': u'1234564'}, unique_ids_)


        self.assertDictEqual(response_body['questionnaire'],
                             {u'geo_code': u"What is the waterpoint's GPS co-ordinates?",
                              u'name': u"What is the waterpoint's last name?",
                              u'firstname': u"What is the waterpoint's first name?",
                              u'short_code': u"What is the waterpoint's Unique ID Number?",
                              u'location': u"What is the waterpoint's location?",
                              u'mobile_number': u"What is the waterpoint's mobile telephone number?"})


    @attr('functional_test')
    def test_should_return_not_found_error_when_unique_id_does_not_exists_for_given_form_code(self):
        response = requests.get(url('/api/unique-id/random/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 404)


    @attr('functional_test')
    def test_should_return_not_found_error_when_for_a_questionnaire_form_code(self):
        response = requests.get(url('/api/unique-id/cli001/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 404)


class TestFailedSubmissionExtraction(unittest.TestCase):

    def setUp(self):
        self.DIGEST_CREDENTIALS = HTTPDigestAuth('tester150411@gmail.com', 'tester150411')
        self.failed_submission_log()

    @classmethod
    def failed_submission_log(cls):
        organization = Mock(spec=Organization)
        organization.org_id = "SLX364903"
        cls.datawinners_log1 = DatawinnerLog(
                message = "12 november 2014 post number 2",
                from_number = "0330307221",
                to_number = "919880734937",
                organization_id = organization.org_id,
                error = "Error. Questionnaire Code Hello is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code. ")

        cls.datawinners_log2 = DatawinnerLog(message = "12 november 2014 post number 2",
                from_number = "0330307221",
                to_number = "919880734937",
                organization_id = organization.org_id,
                error = "Error. Questionnaire Code Hello is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code. ")

        cls.datawinners_log3 = DatawinnerLog(message = "12 november 2014 post number 2",
                from_number = "0330307221",
                to_number = "919880734937",
                organization_id = organization.org_id,
                error = "Error. Questionnaire Code Hello is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code. ")
        cls.datawinners_log1.save()
        cls.datawinners_log2.save()
        cls.datawinners_log3.save()


    def get_data_by_uri(self, uri):
        http_response = requests.get(url(uri), auth=self.DIGEST_CREDENTIALS)
        return json.loads(http_response.content)

    @attr('functional_test')
    def test_should_get_all_failed_submissions(self):
        failed_submission_data = self.get_data_by_uri(
            "/api/get_failed_submissions/")
        submissions = failed_submission_data['submissions']
        self.assertTrue(failed_submission_data['success'])
        self.assertEqual(len(submissions), 3)

    @attr('functional_test')
    def test_should_get_all_failed_submissions_with_start_date(self):
        self.datawinners_log1.created_at = datetime.strptime("2014-11-12", "%Y-%m-%d")
        self.datawinners_log1.save()
        self.datawinners_log2.created_at = datetime.strptime("2014-11-13", "%Y-%m-%d")
        self.datawinners_log2.save()
        self.datawinners_log3.created_at = datetime.strptime("2014-10-13", "%Y-%m-%d")
        self.datawinners_log3.save()
        failed_submission_data = self.get_data_by_uri(
            "/api/get_failed_submissions/?start_date=%s" % '11-11-2014')
        submissions = failed_submission_data['submissions']
        self.assertTrue(failed_submission_data['success'])
        self.assertEqual(len(submissions), 2)

    @attr('functional_test')
    def test_should_get_all_failed_submissions_with_start_date_end_date(self):
        self.datawinners_log1.created_at = datetime.strptime("2014-10-09", "%Y-%m-%d")
        self.datawinners_log1.save()
        self.datawinners_log2.created_at = datetime.strptime("2014-10-11", "%Y-%m-%d")
        self.datawinners_log2.save()
        self.datawinners_log3.created_at = datetime.strptime("2014-10-13", "%Y-%m-%d")
        self.datawinners_log3.save()
        failed_submission_data = self.get_data_by_uri(
            "/api/get_failed_submissions/?start_date=%s&end_date=%s" % ('06-10-2014', '15-10-2014'))
        submissions = failed_submission_data['submissions']
        self.assertTrue(failed_submission_data['success'])
        self.assertEqual(len(submissions), 3)

    def tearDown(self):
        DatawinnerLog.objects.filter(organization="SLX364903").delete()