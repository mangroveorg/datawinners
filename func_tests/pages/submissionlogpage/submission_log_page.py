# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.page import Page
from framework.utils.data_fetcher import *
from pages.submissionlogpage.submission_log_locator import *
from framework.utils.common_utils import *
from tests.submissionlogtests.submission_log_data import UNIQUE_VALUE
import re


class SubmissionLogPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_submission_message(self, sms_data):
        """
        Function to fetch the submission log from the row of the table

        Return submission log
        """
        unique_value = fetch_(UNIQUE_VALUE, from_(sms_data))
        return self.driver.find(by_xpath(SUBMISSION_LOG_TR_XPATH % unique_value)).text

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

    def choose_delete_on_the_action_dropdown(self):
        self.driver.find(ACTION_SELECT_CSS_LOCATOR).click()
        self.driver.find(DELETE_BUTTON).click()

    def check_all_submissions(self):
        self.driver.find(CHECKALL_CB_CSS_LOCATOR).click()

    def get_all_data_on_nth_column(self, column):
        column_data = []
        index = 1
        while index <= self.get_shown_records_count():
            column_data.append(self.get_cell_data(index, column))
            index += 1
        return column_data

    def get_shown_records_count(self):
        try:
            datatable_info = self.driver.find(SHOWN_RECORDS_COUNT_CSS_LOCATOR).text
            [begin, end] = re.findall('\d+', datatable_info)
            return int(end) - int(begin) + 1
        except Exception:
            return 0

    def get_cell_data(self, row, col):
        locator = by_xpath(XPATH_TO_CELL % (str(row), str(col)))
        return self.driver.find(locator).text

    def click_on_nth_header(self, index):
        self.driver.find(by_css(HEADER_CELL_CSS_LOCATOR % str(index))).click()

    def click_on_success_tab(self):
        self.driver.find(SUCCESS_TAB_CSS_LOCATOR).click()