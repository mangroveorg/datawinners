# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.common_utils import generateId
from pages.page import Page
from framework.utils.data_fetcher import *
from pages.adddatasenderspage.add_data_senders_locator import *
from tests.alldatasenderstests.add_data_senders_data import *
from tests.alldatasenderstests.all_data_sender_data import REGISTRATION_SUCCESS_MESSAGE_TEXT
from tests.testsettings import UI_TEST_TIMEOUT


class AddDataSenderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def select_web_device(self):
        self.driver.find(WEB_CB).click()

    def enter_email(self, registration_data):
        email_address_prefix = fetch_(EMAIL_ADDRESS, from_(registration_data))
        generated_email_address = email_address_prefix + generateId() + "@abc.com"
        self.driver.find_text_box(EMAIL_TB).enter_text(generated_email_address)

    def enter_data_sender_details_from(self, registration_data, unique_id=None, email=None):
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

        if email is not None:
            self.driver.find(by_css("#id_devices_1")).click()
            self.driver.find_text_box(EMAIL_TB).enter_text(email)

        if unique_id is not None:
            self.set_unique_id(unique_id)
        self.driver.find(REGISTER_BTN).click()
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css("span.loading"))
        return self

    def get_registered_datasender_id(self):
        message = self.get_success_message()
        assert REGISTRATION_SUCCESS_MESSAGE_TEXT in message
        data_sender_id = self._parse(message)
        return data_sender_id

    def _parse(self, message):
        return message.split(' ')[-1]

    def get_error_message(self):
        """
        Function to fetch the error messages from error label of the add data sender page

        Return error message
        """
        error_message = ""
        self.driver.wait_for_element(UI_TEST_TIMEOUT, ERROR_MESSAGE_LABEL, True)
        locators = self.driver.find_elements_(ERROR_MESSAGE_LABEL)
        if locators:
            for locator in locators:
                error_message = error_message + locator.text
        return error_message.replace("\n", " ")

    def get_success_message(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT, FLASH_MESSAGE_LABEL, want_visible=True)
        return locator.text

    def open_import_lightbox(self):
        if not self.is_in_project_level():
            return False

        self.driver.find(OPEN_IMPORT_DIALOG_LINK).click()
        from pages.lightbox.import_datasender_light_box_page import ImportDatasenderLightBox

        return ImportDatasenderLightBox(self.driver)


    def is_in_project_level(self):
        return self.driver.get_title() in [u"Projet - Expéditeurs", u"Projects - Data Senders"]

    def set_unique_id(self, unique_id):
        checkbox_unique_id = self.driver.find(CB_LET_US_GENERATE_ID_FOR_U)
        if checkbox_unique_id.get_attribute("checked") == "true":
            checkbox_unique_id.click()
        self.driver.find_text_box(UNIQUE_ID_TB_LOCATOR).enter_text(unique_id)

    def unique_id_check_box_is_checked(self):
        return self.driver.find(CB_LET_US_GENERATE_ID_FOR_U).get_attribute("checked") == u"true"

    def unique_id_field_is_enabled(self):
        return self.driver.find_text_box(UNIQUE_ID_TB_LOCATOR).is_enabled

    def datasender_has_web_access(self):
        return self.driver.is_element_present(by_id("email-li"))

    def enter_datasender_mobile_number(self, mobile_number):
        self.driver.find_text_box(MOBILE_NUMBER_TB).enter_text(mobile_number)

    def navigate_to_datasender_page(self):
        self.driver.find(by_id("cancel")).click()

    def click_submit_button(self):
        self.driver.find(REGISTER_BTN).click()