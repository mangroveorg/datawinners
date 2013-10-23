# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from framework.utils.common_utils import CommonUtilities
from pages.smstesterpage.sms_tester_locator import *
from pages.page import Page
from framework.utils.data_fetcher import *
from tests.smstestertests.sms_tester_data import *
from tests.testsettings import UI_TEST_TIMEOUT


class SMSTesterPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def send_sms_with(self, sms_data):
        """
        Function to enter and send the data using sms player

        Args:
        sms_data is data to fill in the different fields like To, From and SMS field

        Return self
        """
        self.driver.find_text_box(TO_TB).enter_text(fetch_(RECEIVER, from_(sms_data)))
        self.driver.find_text_box(FROM_TB).enter_text(fetch_(SENDER, from_(sms_data)))
        self.driver.find_text_box(SMS_TA).enter_text(fetch_(SMS, from_(sms_data)))
        self.driver.find(SEND_SMS_BTN).click()
        return self

    def send_valid_sms_with(self, sms_data):
        self.send_sms_with(sms_data)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("flash-message"), True)

    def get_response_message(self):
        """
        Function to fetch the success/error response message from flash label of the page

        Return success/error message
        """
        comm_utils = CommonUtilities(self.driver)
        comm_utils.wait_for_element(20, FLASH_MSG_LABEL)
        return self.driver.find(FLASH_MSG_LABEL).text

    def get_error_message(self):
        """
        Function to fetch the error messages from error label of the login
        page

        Return error message
        """
        error_message = ""
        comm_utils = CommonUtilities(self.driver)
        comm_utils.wait_for_element(10, ERROR_MESSAGE_LABEL)
        locators = self.driver.find_elements_(ERROR_MESSAGE_LABEL)
        if locators:
            for locator in locators:
                error_message = error_message + locator.text
        return error_message.replace("\n", " ")
