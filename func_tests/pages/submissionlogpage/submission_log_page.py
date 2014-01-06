# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
import time

from pages.page import Page
from framework.utils.data_fetcher import *
from pages.submissionlogpage.submission_log_locator import *
from tests.submissionlogtests.submission_log_data import UNIQUE_VALUE
from tests.testsettings import UI_TEST_TIMEOUT
from framework.exception import CouldNotLocateElementException

DAILY_DATE_RANGE = "daily_date_range"
MONTHLY_DATE_RANGE = "month_date_range"
CURRENT_MONTH = "current_month"
LAST_MONTH = "last_month"
YEAR_TO_DATE = "year_to_date"
ALL_PERIODS = "all_periods"


class SubmissionLogPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.date_range_dict = {CURRENT_MONTH: CURRENT_MONTH_LABEL,
                        LAST_MONTH: LAST_MONTH_LABEL,
                        YEAR_TO_DATE: YEAR_TO_DATE_LABEL,
                        DAILY_DATE_RANGE: DAILY_DATE_RANGE_LABEL,
                        MONTHLY_DATE_RANGE: MONTHLY_DATE_RANGE_LABEL,
                        ALL_PERIODS:ALL_PERIODS_LABEL}

    def get_submission_message(self, sms_data):
        """
        Function to fetch the submission log from the row of the table

        Return submission log
        """
        unique_value = fetch_(UNIQUE_VALUE, from_(sms_data))

        columns = self.driver.find_elements_by_xpath(SUBMISSION_LOG_TR_XPATH % unique_value)
        logs = []
        for column in columns:
            column.click()
            logs.append(column.text)
        submission_log = ' '.join(logs)
        return submission_log.strip()

    def get_failure_message(self, sms_data):
        """
        Function to fetch the submission log from the row of the table

        Return submission log
        """
        unique_value = fetch_(UNIQUE_VALUE, from_(sms_data))
        failure_msg_xpath = SUBMISSION_LOG_TR_XPATH + SUBMISSION_LOG_FAILURE_MSG_XPATH
        return self.driver.find(by_xpath(failure_msg_xpath % unique_value)).get_attribute("title")

    def get_active_tab_text(self):
        return self.driver.find(ACTIVE_TAB_LOCATOR).text

    def choose_on_dropdown_action(self, action_button):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ACTION_SELECT_CSS_LOCATOR, True)
        self.driver.find(ACTION_SELECT_CSS_LOCATOR).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, action_button, True)
        self.driver.find(action_button).click()

    def check_all_submissions(self):
        self.driver.find(CHECKALL_CB_CSS_LOCATOR).click()

    def get_all_data_on_nth_column(self, column):
        column_data = []
        index = 2
        while index <= self.get_total_number_of_records():
            column_data.append(self.get_cell_value(index, column))
            index += 1
        return column_data

    def get_all_data_on_nth_row(self, row, header_count):
        row_data = []
        time.sleep(2)
        for col in range(2, header_count + 1):
            row_data.append(self.get_cell_value(row, col))
        return row_data

    def click_on_nth_header(self, index):
        self.driver.find(by_css(HEADER_CELL_CSS_LOCATOR % str(index))).click()

    def click_on_success_tab(self):
        self.driver.find(SUCCESS_TAB_CSS_LOCATOR).click()

    def click_action_button(self):
        buttons = self.driver.find(by_css("#submission_logs")).find_elements(by="css selector", value="button.action")
        buttons[1].click()

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def check_submission_by_row_number(self, row_number):
        self.driver.find(by_css(SUBMISSION_CB_LOCATOR % str(row_number+1))).click()

    def is_checkall_checked(self):
        return self.driver.find(CHECKALL_CB_CSS_LOCATOR).get_attribute("checked") == "true"

    def is_checkall_enabled(self):
        return self.driver.find(CHECKALL_CB_CSS_LOCATOR).is_enabled()

    def empty_help_text(self):
        return self.driver.find(by_css('.submission_table .help_accordion')).text

    def wait_for_table_data_to_load(self):
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".dataTables_processing"))

    def search(self, search_text):
        self.driver.find_text_box(by_css("#search_text")).enter_text(search_text)
        self.wait_for_table_data_to_load()

    def filter_by_datasender(self,datasender):
        self.driver.find_text_box(by_css("#data_sender_filter")).enter_text(datasender)
        try:
            (self.driver.find(by_xpath(DS_AND_SUBJECT_FILTER_LOCATOR_BY_NAME %datasender))).click()
        except CouldNotLocateElementException:
            time.sleep(1)
            (self.driver.find(by_xpath(DS_AND_SUBJECT_FILTER_LOCATOR_BY_ID %datasender))).click()

    def filter_by_subject(self, subject):
        self.driver.find_text_box(by_css("#subject_filter")).enter_text(subject)
        try:
            (self.driver.find(by_xpath(DS_AND_SUBJECT_FILTER_LOCATOR_BY_NAME %subject))).click()
        except CouldNotLocateElementException:
            time.sleep(1)
            (self.driver.find(by_xpath(DS_AND_SUBJECT_FILTER_LOCATOR_BY_ID %subject))).click()

    def get_cell_value(self, row, column):
        #row+1 for ignoring extra row for select all msg
        return self.driver.find(by_xpath(".//*[@class='submission_table']/tbody/tr[%s]/td[%s]" % ((row +1), column))).text

    def get_total_number_of_rows(self):
        return self.driver.find_elements_(by_xpath(".//table[@class='submission_table']/tbody/tr")).__len__()

    def get_total_number_of_records(self):
        return self.driver.find_elements_(by_css(".row_checkbox")).__len__()

    def get_empty_datatable_text(self):
        return self.driver.find(EMPTY_TABLE_MSG_ROW).text

    def filter_by_reporting_date(self, type):
        self.driver.find(by_css('#reportingPeriodPicker')).click()
        self.driver.wait_for_element(20, self.date_range_dict.get(type), want_visible=True).click()
        if type == DAILY_DATE_RANGE:
            buttons = self.driver.find_elements_(BTN_DONE_)
            time.sleep(1)
            buttons[1].click()

    def filter_by_reporting_month(self, type):
        self.driver.find(by_css('#reportingPeriodPicker')).click()
        self.driver.wait_for_element(20, self.date_range_dict.get(type), want_visible=True).click()
        if type == MONTHLY_DATE_RANGE:
            buttons = self.driver.find_elements_(BTN_DONE_)
            time.sleep(1)
            buttons[1].click()

    def filter_by_submission_date(self, type):
        self.driver.find(by_css('#submissionDatePicker')).click()
        self.driver.wait_for_element(20, self.date_range_dict.get(type), want_visible=True).click()
        if type == DAILY_DATE_RANGE:
            buttons = self.driver.find_elements_(BTN_DONE_)
            time.sleep(1)
            buttons[0].click()


