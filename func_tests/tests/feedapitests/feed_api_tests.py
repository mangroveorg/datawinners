from datetime import datetime
import os
import time
import unittest
import urllib2
from django.utils.unittest.case import SkipTest
import jsonpickle
from nose.plugins.attrib import attr
import requests
from framework.base_test import setup_driver, teardown_driver, HeadlessRunnerTest
from framework.utils.common_utils import by_css, by_xpath
from framework.utils.data_fetcher import fetch_, from_
from pages.questionnairetabpage.questionnaire_tab_page import QuestionnaireTabPage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.loginpage.login_page import LoginPage, login
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON, DELETE_BUTTON
from pages.warningdialog.warning_dialog import WarningDialog
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_DASHBOARD_PAGE, get_test_port
from tests.projects.questionnairetests.project_questionnaire_data import WATERPOINT_QUESTIONNAIRE_DATA, WATERPOINT_PROJECT_DATA
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.smstestertests.sms_tester_data import MESSAGE
from tests.submissionlogtests.edit_survey_response_data import ANSWERS_TO_BE_SUBMITTED, EDITED_ANSWERS, get_errorred_sms_data_with_questionnaire_code

DATE_FORMAT = '%d-%m-%Y %H:%M:%S'


def sleep_until(f, timeout):
    for i in xrange(timeout):
        if f():
            break
        else:
            time.sleep(1000)


class TestFeeds(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        cls.navigation_page = login(cls.driver)
        cls.project_overview_page = cls._create_project()

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @classmethod
    def _create_project(cls):
        cls.dashboard_page = DashboardPage(cls.driver)
        create_questionnaire_options_page = cls.dashboard_page.navigate_to_create_project_page()
        create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(WATERPOINT_PROJECT_DATA,WATERPOINT_QUESTIONNAIRE_DATA)
        return create_questionnaire_page.save_and_create_project_successfully()

    def _submit_success_data(self, project_name):
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        view_all_project_page = self.navigation_page.navigate_to_view_all_project_page()
        project_overview_page = view_all_project_page.navigate_to_project_overview_page(project_name)

        submission_page = project_overview_page.navigate_to_web_questionnaire_page()
        submission_page.fill_and_submit_answer(ANSWERS_TO_BE_SUBMITTED)
        self.driver.create_screenshot("api_feed_sub_success.png")
        self.assertEqual(submission_page.get_success_message(), "Successfully submitted", "Web submission failed")


    def _edit_data(self):
        analysis_page = self.project_overview_page.navigate_to_data_page()
        submission_log_page = analysis_page.navigate_to_all_data_record_page()
        submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(EDIT_BUTTON)
        submission_page = WebSubmissionPage(self.driver)
        submission_page.fill_and_submit_answer(EDITED_ANSWERS)
        self.assertEqual(submission_page.get_success_message(), "Your changes have been saved.", "Edit of web submission failed")

    def _get_encoded_date(self):
        date = datetime.utcnow()
        date = urllib2.quote(date.strftime(DATE_FORMAT).encode("utf-8"))
        return date

    def get_feed_response(self, questionnaire_code, start_date, end_date):
        url = "http://localhost:" + get_test_port() + "/feeds/" + questionnaire_code + "?start_date=" + start_date + "&end_date=" + end_date
        actual_data = requests.get(url, auth=('tester150411@gmail.com', 'tester150411' ))
        response_list = jsonpickle.decode(actual_data.content)
        return response_list

    def _submit_errorred_data(self, questionnaire_code):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        page = SMSTesterPage(self.driver)
        sms_data = get_errorred_sms_data_with_questionnaire_code(questionnaire_code)
        page.send_sms_with(sms_data)
        self.assertTrue(fetch_(MESSAGE, from_(sms_data)) in page.get_response_message())


    def delete_submission(self):
        analysis_page = self.project_overview_page.navigate_to_data_page()
        submission_log_page = analysis_page.navigate_to_all_data_record_page()
        self.driver.wait_until_element_is_not_present(20, by_css("loading")) #wait for table to load
        self.driver.find(by_xpath("//table[@class='submission_table']//td[text()='admin1']/../td/input")).click()
        #submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(DELETE_BUTTON)
        warning_dialog = WarningDialog(self.driver)
        warning_dialog.confirm()


    def assert_feed_values(self, feed_entry, expected_data, reporter_id, status):
        self.assertDictEqual(feed_entry['values'], expected_data)
        self.assertEquals(reporter_id, feed_entry['data_sender_id'])
        self.assertRegexpMatches(feed_entry['feed_modified_time'],
                                 '\d{4}-\d{2}-\d{2}\W\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}\:\d{2}')
        self.assertRegexpMatches(feed_entry['submission_modified_time'],
                                 '\d{4}-\d{2}-\d{2}\W\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}\:\d{2}')
        self.assertEquals(feed_entry['status'], status)


    @attr('functional_test')
    def test_feeds(self):
        start_date = self._get_encoded_date()
        questionnaire_code = self.project_overview_page.get_questionnaire_code()
        project_name = self.project_overview_page.get_project_title()

        self._submit_errorred_data(questionnaire_code)
        end_date = self._get_encoded_date()
        sleep_until(lambda: len(self.get_feed_response(questionnaire_code, start_date, end_date)) > 0, 30)
        response_list = self.get_feed_response(questionnaire_code, start_date, end_date)
        self.assertEquals(1, len(response_list))
        feed_entry = response_list[-1]
        expected_data = {'q3': '5', 'q2': 'wp01', 'q5': 'a', 'q4': '25.12.2010', 'q7': 'f', 'q6': 'admin', 'q8': '12,12'}
        status = "error"
        reporter_id = "rep276"
        self.assert_feed_values(feed_entry, expected_data, reporter_id, status)

        self._submit_success_data(project_name)
        end_date = self._get_encoded_date()
        sleep_until(lambda: len(self.get_feed_response(questionnaire_code, start_date, end_date)) == 2, 30)
        response_list = self.get_feed_response(questionnaire_code, start_date, end_date)
        self.assertEquals(2, len(response_list))
        feed_entry = response_list[-1]
        expected_data = {'q2': {'deleted': False, 'id': 'wp01', 'name': 'Test'}, 'q3': '5.0', 'q5': ['a'], 'q4': '24.12.2010', 'q7': ['b'],
                         'q6': 'admin', 'q8': '12.0,12.0'}
        rep_id = "rep276"
        status = "success"
        self.assert_feed_values(feed_entry, expected_data, rep_id, status)

        self._edit_data()
        end_date = self._get_encoded_date()
        sleep_until(lambda: len(self.get_feed_response(questionnaire_code, start_date, end_date)) == 2, 30)
        edited_response_list = self.get_feed_response(questionnaire_code, start_date, end_date)
        self.assertEquals(2, len(edited_response_list))
        edited_feed_entry = edited_response_list[-1]
        expected_data_after_edit = {"q3": "8.0", "q2": {"deleted": False, "id": "wp01", "name": "Test"},
                                    "q5": ["b"], "q4": "24.12.2012",  "q7": ["a", "b"], "q6": "admin1",
                                    "q8": "-18,27"}
        self.assert_feed_values(edited_feed_entry, expected_data_after_edit, rep_id, status)

        self.delete_submission()
        end_date = self._get_encoded_date()
        sleep_until(lambda: len(self.get_feed_response(questionnaire_code, start_date, end_date)) == 2, 30)
        response_list_after_delete = self.get_feed_response(questionnaire_code, start_date, end_date)
        self.assertEquals(2, len(response_list_after_delete))
        deleted_feed_entry = response_list_after_delete[-1]
        expected_data_after_delete = {'q2': {"deleted": False, "id": "wp01", "name": "Test"}, 'q3': '8.0', 'q5': ['b'], 'q4': '24.12.2012',
                                      'q7': ['a', 'b'],
                                      'q6': 'admin1', 'q8': '-18,27'}
        status = "deleted"
        self.assert_feed_values(deleted_feed_entry, expected_data_after_delete, rep_id, status)





