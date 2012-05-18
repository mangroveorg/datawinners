# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.common_utils import generateId
from pages.page import Page
from framework.utils.data_fetcher import *
from pages.adddatasenderspage.add_data_senders_locator import *
from tests.adddatasenderstests.add_data_senders_data import *


class AddDataSenderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def select_web_device(self):
        self.driver.find(WEB_CB).click()

    def enter_email(self, registration_data):
        email_address_prefix = fetch_(EMAIL_ADDRESS, from_(registration_data))
        generated_email_address = email_address_prefix + generateId() + "@abc.com"
        self.driver.find_text_box(EMAIL_TB).enter_text(generated_email_address)

    def add_data_sender_with(self, registration_data):
        """
        Function to enter and submit the data on add data sender page

        Args:
        registration_data is data to fill in the different fields like first
        name, last name, telephone number and commune

        Return self
        """
        self.driver.find_text_box(NAME_TB).enter_text(
            fetch_(NAME, from_(registration_data)))
        self.driver.find_text_box(MOBILE_NUMBER_TB).enter_text(
            fetch_(MOBILE_NUMBER, from_(registration_data)))
        self.driver.find_text_box(COMMUNE_TB).enter_text(
            fetch_(COMMUNE, from_(registration_data)))
        self.driver.find_text_box(GPS_TB).enter_text(
            fetch_(GPS, from_(registration_data)))
        self.driver.find(REGISTER_BTN).click()
        return self

    def get_error_message(self):
        """
        Function to fetch the error messages from error label of the add data sender page

        Return error message
        """
        error_message = ""
        locators = self.driver.find_elements_(ERROR_MESSAGE_LABEL)
        if locators:
            for locator in locators:
                error_message = error_message + locator.text
        return error_message.replace("\n", " ")

    def get_success_message(self):
        """
        Function to fetch the success message from flash label of the add data sender page

        Return success message
        """
        error_message = ""
        locator = self.driver.find(FLASH_MESSAGE_LABEL)
        return locator.text
