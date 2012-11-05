# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.page import Page
from framework.utils.data_fetcher import *
from pages.submissionlogpage.submission_log_locator import *
from framework.utils.common_utils import *
from tests.submissionlogtests.submission_log_data import UNIQUE_VALUE


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
