# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
import time

from pages.page import Page
from framework.utils.data_fetcher import *
from pages.submissionlogpage.submission_log_locator import *
from tests.submissionlogtests.submission_log_data import UNIQUE_VALUE
from tests.testsettings import UI_TEST_TIMEOUT


class SubmissionLogPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

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
        index = 1
        while index <= self.get_shown_records_count():
            column_data.append(self.get_cell_data(index, column))
            index += 1
        return column_data

    def get_all_data_on_nth_row(self, row, header_count):
        row_data = []
        time.sleep(2)
        for col in range(2, header_count + 1):
            row_data.append(self.get_cell_data(row, col))
        return row_data

    def get_shown_records_count(self):
        try:
            datatable_info = self.driver.find(SHOWN_RECORDS_COUNT_CSS_LOCATOR).text
            [begin, end] = re.findall('\d+', datatable_info)
            return int(end) - int(begin) + 1
        except Exception:
            return 0

    def get_total_count_of_records(self):
        return self.driver.find(TOTAL_RECORDS_COUNT).text

    def get_cell_data(self, row, col):
        locator = by_xpath(XPATH_TO_CELL % (str(row), str(col)))
        return self.driver.find(locator).text

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

    def is_filter_enabled(self):
        return self.driver.find(SUBMISSION_DATE_FILTER).is_enabled()

    def empty_help_text(self):
        return self.driver.find(by_css('.submission_table .help_accordion')).text

    def wait_for_table_data_to_load(self):
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".dataTables_processing"))

    def search(self, search_text):
        self.driver.find_text_box(by_css("#search_text")).enter_text(search_text)
        self.wait_for_table_data_to_load()

    def get_cell_value(self, row, column):
        return self.driver.find(by_xpath(".//*[@class='submission_table']/tbody/tr[%s]/td[%s]" % ((row +1), column))).text