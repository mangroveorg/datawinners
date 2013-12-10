# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datetime import datetime
import time
from django.utils.unittest.case import SkipTest

from nose.plugins.attrib import attr
from selenium.webdriver.support.wait import WebDriverWait

from framework.base_test import setup_driver, teardown_driver
from framework.exception import CouldNotLocateElementException
from framework.utils.common_utils import by_css, by_xpath
from framework.utils.data_fetcher import fetch_, from_
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatapage.all_data_page import AllDataPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from pages.allsubjectspage.all_subject_type_page import AllSubjectTypePage
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from pages.loginpage.login_page import LoginPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.submissionlogpage.submission_log_locator import DELETE_BUTTON, ACTION_SELECT_CSS_LOCATOR
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ALL_DATA_SENDERS_PAGE, ALL_DATA_PAGE, DATA_WINNER_SMS_TESTER_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.submissionlogtests.submission_log_data import *
from pages.warningdialog.warning_dialog import WarningDialog
from tests.testsettings import UI_TEST_TIMEOUT
from tests.websubmissiontests.web_submission_data import DEFAULT_ORG_DATA


@attr('suit_3')
class TestSubmissionLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        cls.dashboard = login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.URL = None

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def get_submission_log_page(self):
        if self.URL:
            self.driver.go_to(self.URL)
            submission_log_page = SubmissionLogPage(self.driver)
        else:
            submission_log_page = self.go_to_submission_log_page()
        return submission_log_page

    @classmethod
    def go_to_submission_log_page(cls, project_name=FIRST_PROJECT_NAME, cache_url=True):
        cls.driver.go_to(ALL_DATA_PAGE)
        submission_log_page = AllDataPage(cls.driver).navigate_to_submission_log_page(project_name)
        if not cls.URL and cache_url:
            cls.URL = cls.driver.current_url
        return submission_log_page

    @SkipTest
    @attr('functional_test')
    def test_should_show_warning_when_deleting_records(self):
        submission_log_page = self.get_submission_log_page()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ACTION_SELECT_CSS_LOCATOR, True)

        time.sleep(5) # instead, check for other checkboxes value
        submission_log_page.check_all_submissions()
        WebDriverWait(self.driver, UI_TEST_TIMEOUT, 1, (CouldNotLocateElementException)).until(
            lambda x: x.find(by_css(".selected_submissions")).is_selected())
        submission_log_page.choose_on_dropdown_action(DELETE_BUTTON)
        warning_dialog = WarningDialog(self.driver)
        self.assertEqual(DELETE_SUBMISSION_WARNING_MESSAGE, warning_dialog.get_message())

    @SkipTest
    @attr('functional_test')
    def test_sorting_in_submission_log_page(self):
        submission_log_page = self.get_submission_log_page()
        self.verify_sort_data_by_submission_date_by_default(submission_log_page)
        self.verify_sort_data_alphanumerically_for_other_column_than_submission_date(submission_log_page)

    def verify_sort_data_alphanumerically_for_other_column_than_submission_date(self, submission_log_page):
        submission_log_page.click_on_nth_header(8)
        self.assertEqual(submission_log_page.get_all_data_on_nth_column(8), EXPECTED_FA_SORTED)

    def verify_sort_data_by_submission_date_by_default(self, submission_log_page):
        submission_dates = submission_log_page.get_all_data_on_nth_column(3)
        self.assertTrue(len(submission_dates) >= 3)
        SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG = "%b. %d, %Y, %I:%M %p"
        for index, submission_date in enumerate(submission_dates[1:-1]):
            before = datetime.strptime(submission_dates[index], SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
            current = datetime.strptime(submission_date, SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
            after = datetime.strptime(submission_dates[index + 2], SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
            self.assertTrue(before >= current >= after)

    @SkipTest
    @attr('functional_test')
    def test_should_have_consistent_sorting_on_each_tabs_submission_log_page(self):
        submission_log_page = self.get_submission_log_page()
        time.sleep(2)
        submission_log_page.click_on_nth_header(8)
        submission_log_page.click_on_success_tab()
        time.sleep(6)
        self.assertEqual(submission_log_page.get_all_data_on_nth_column(7), EXPECTED_FA_SORTED)

    @SkipTest
    @attr('functional_test')
    def test_should_load_actions_dynamically(self):
        submission_log_page = self.get_submission_log_page()
        time.sleep(2)
        submission_log_page.click_action_button()
        self.assert_none_selected_shown(submission_log_page)
        time.sleep(1)
        submission_log_page.check_submission_by_row_number(3)
        submission_log_page.click_action_button()
        self.assert_action_menu_shown_for(submission_log_page)

        submission_log_page.check_submission_by_row_number(3)
        submission_log_page.click_action_button()
        self.assert_none_selected_shown(submission_log_page)

    def assert_none_selected_shown(self, submission_log_page):
        self.assertTrue(submission_log_page.is_none_selected_shown())
        self.assertFalse(submission_log_page.actions_menu_shown())

    def assert_action_menu_shown_for(self, submission_log_page):
        self.assertTrue(submission_log_page.actions_menu_shown())
        self.assertFalse(submission_log_page.is_none_selected_shown())

    @SkipTest
    @attr("functional_test")
    def test_should_disable_checkall_cb__and_filters_if_there_is_no_submission(self):

        submission_log_page = self.go_to_submission_log_page("project having people as subject", cache_url=False)
        self.assertFalse(submission_log_page.is_checkall_enabled())
        self.assertFalse(submission_log_page.is_filter_enabled())

    @SkipTest
    @attr("functional_test")
    def test_should_check_checkall_cb_when_all_cb_are_checked(self):
        submission_log_page = self.get_submission_log_page()
        submission_log_page.check_all_submissions()
        self.assertTrue(submission_log_page.is_checkall_checked())
        submission_log_page.check_submission_by_row_number(3)
        self.assertFalse(submission_log_page.is_checkall_checked())
        submission_log_page.check_submission_by_row_number(3)
        self.assertTrue(submission_log_page.is_checkall_checked())

    def register_datasender(self, datasender_details, all_datasenders_page, id=None):
        add_data_sender_page = all_datasenders_page.navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(datasender_details, unique_id=id)
        return add_data_sender_page.get_registered_datasender_id() if id is None else id


    @attr("functional_test")
    def test_should_update_submission_log_when_DS_info_is_edited(self):
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_datasenders_page = AllDataSendersPage(self.driver)
        ds_id = self.register_datasender(DATASENDER_DETAILS, all_datasenders_page)

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_valid_sms_with(VALID_DATA)

        message = sms_tester_page.get_response_message()
        self.assertTrue(fetch_(SUCCESS_MESSAGE, VALID_DATA) in message, "message:" + message)

        submission_log_page = self.go_to_submission_log_page()
        submission_log_page.search(ds_id)
        self.assertTrue(DATASENDER_DETAILS[NAME] in submission_log_page.get_cell_value(row=1, column=2))

        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_datasenders_page.search_with(ds_id)
        all_datasenders_page.wait_for_table_to_load()

        all_datasenders_page.select_a_data_sender_by_id(ds_id)
        all_datasenders_page.select_edit_action()
        AddDataSenderPage(self.driver).enter_data_sender_details_from(EDITED_DATASENDER_DETAILS)
        submission_log_page = self.go_to_submission_log_page()
        submission_log_page.search(ds_id)
        self.assertTrue(EDITED_DATASENDER_DETAILS[NAME] in submission_log_page.get_cell_value(row=1, column=2))

    @attr("functional_test")
    def test_should_update_submission_log_when_subject_info_is_edited(self):
        self.dashboard.navigate_to_all_subject_page()
        all_subject_type_page = AllSubjectTypePage(self.driver)
        add_subject_page = all_subject_type_page.select_subject_type('Clinic').navigate_to_register_subject_page()

        add_subject_page.add_subject_with(VALID_DATA_FOR_SUBJECT)
        add_subject_page.submit_subject()
        message = fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_FOR_SUBJECT))

        flash_message = add_subject_page.get_flash_message()
        self.assertIn(message, flash_message)
        subject_short_code = flash_message.replace(message, '')

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        VALID_SMS_FOR_EDIT_SUBJECT[SMS] = VALID_SMS_FOR_EDIT_SUBJECT[SMS].replace('short_code', subject_short_code, 1)
        sms_tester_page.send_valid_sms_with(VALID_SMS_FOR_EDIT_SUBJECT)

        submission_log_page = self.go_to_submission_log_page()
        submission_log_page.search(subject_short_code)
        self.assertIn(fetch_(SUB_LAST_NAME, VALID_DATA_FOR_SUBJECT), submission_log_page.get_cell_value(1, 5))

        self.dashboard.navigate_to_all_subject_page()
        all_subject_type_page = AllSubjectTypePage(self.driver)
        add_subject_page = all_subject_type_page.select_subject_type('Clinic').navigate_to_register_subject_page()

        add_subject_page.navigate_to_subject_list()
        subject_list_page = AllSubjectsListPage(self.driver)
        subject_list_page.select_subject_by_id(subject_short_code)
        edit_subject_page = subject_list_page.click_edit_action_button()
        edit_subject_page.add_subject_with(VALID_DATA_FOR_EDIT)
        edit_subject_page.submit_subject()

        submission_log_page = self.go_to_submission_log_page()
        submission_log_page.search(subject_short_code)
        self.assertIn(fetch_(SUB_LAST_NAME, VALID_DATA_FOR_EDIT), submission_log_page.get_cell_value(1, 5))

    def make_web_submission(self):
        all_data_page = self.dashboard.navigate_to_all_data_page()
        web_submission_page = all_data_page.navigate_to_web_submission_page(
            fetch_("project_name", from_(DEFAULT_ORG_DATA)))
        self.driver.wait_for_page_with_title(5, web_submission_page.get_title())
        web_submission_page.fill_questionnaire_with(VALID_SUBMISSION)
        web_submission_page.submit_answers()

    @attr("functional_test")
    def test_should_filter_by__name_and_id_of_datasender_and_subject(self):

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_page.send_valid_sms_with(SMS_REGISTER_SUBJECT)
        sms_tester_page.send_valid_sms_with(SMS_WEB_SUBMISSION)

        submission_log_page = self.go_to_submission_log_page()

        datasender_name = 'Tester'
        submission_log_page.filter_by_datasender(datasender_name)
        submission_log_page.wait_for_table_data_to_load()
        self._verify_filtered_records_by_datasender_name_or_id(datasender_name, submission_log_page)

        project_name = fetch_("last_name", from_(SUBJECT_DATA))
        submission_log_page.filter_by_subject(project_name)
        submission_log_page.wait_for_table_data_to_load()
        self._verify_filtered_records_by_subject_name_or_id(project_name, submission_log_page)

        datasender_id = 'rep276'
        submission_log_page.filter_by_datasender(datasender_id)
        submission_log_page.wait_for_table_data_to_load()
        self._verify_filtered_records_by_datasender_name_or_id(datasender_id, submission_log_page)

        project_short_code = fetch_("short_code", from_(SUBJECT_DATA))
        submission_log_page.filter_by_subject(project_short_code)
        submission_log_page.wait_for_table_data_to_load()
        self._verify_filtered_records_by_subject_name_or_id(project_short_code, submission_log_page)

    def _verify_filtered_records_by_datasender_name_or_id(self, datasender, submission_log_page):
        total_number_of_rows = submission_log_page.get_total_number_of_records()
        for i in range(1, total_number_of_rows):
            self.assertIn(datasender, submission_log_page.get_cell_value(i, 2))

    def _verify_filtered_records_by_subject_name_or_id(self, project, submission_log_page):
        total_number_of_rows = submission_log_page.get_total_number_of_records()
        for i in range(1, total_number_of_rows):
            self.assertIn(project, submission_log_page.get_cell_value(i, 5))
