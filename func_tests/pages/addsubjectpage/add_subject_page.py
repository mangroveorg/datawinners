# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from framework.utils.common_utils import generateId, CommonUtilities
from pages.datasenderpage.data_sender_locator import SMARTPHONE_NAV
from pages.page import Page
from framework.utils.data_fetcher import *
from pages.addsubjectpage.add_subject_locator import *
from pages.smartphoneinstructionpage.smart_phone_instruction_page import SmartPhoneInstructionPage
from pages.websubmissionpage.web_submission_locator import SECTION_TITLE, BACK_TO_PROJECT_LINK
from tests.addsubjecttests.add_subject_data import *


class AddSubjectPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def add_subject_with(self, addition_data):
        """
        Function to fill addition_data with random short name and submit on add a subject page

        Args:
        registration_data is addition_data to fill in the different fields like short name, location, Geo Code,
        description and mobile number

        Return flash message
        """
        short_name = fetch_(SUB_UNIQUE_ID, from_(addition_data))
        if short_name is not None:
            self.driver.find(AUTO_GENERATE_CB).click()
            short_name = short_name + generateId()
            self.driver.find_text_box(UNIQUE_ID_TB).enter_text(short_name)
        self.driver.find_text_box(FNAME_TB).enter_text(
            fetch_(SUB_FIRST_NAME, from_(addition_data)))
        self.driver.find_text_box(LNAME_TB).enter_text(
            fetch_(SUB_LAST_NAME, from_(addition_data)))
        self.driver.find_text_box(LOCATION_TB).enter_text(
            fetch_(LOCATION, from_(addition_data)))
        self.driver.find_text_box(GEO_CODE_TB).enter_text(
            fetch_(GPS, from_(addition_data)))
        self.driver.find_text_box(MOBILE_NUMBER_TB).enter_text(
            fetch_(MOBILE_NUMBER, from_(addition_data)))

#    def add_subject_with(self, addition_data):
#        """
#        Function to fill and submit data on add a subject page
#
#        Args:
#        addition_data is data to fill in the different fields like short name, location, Geo Code,
#        description and mobile number
#
#        Return self
#        """
#        entity_type = fetch_(ENTITY_TYPE, from_(addition_data))
#        self.driver.find_drop_down(ENTITY_TYPE_DD).set_selected(entity_type)
#        self.driver.find_text_box(NAME_TB).enter_text(
#            fetch_(NAME, from_(addition_data)))
#        short_name = fetch_(SHORT_NAME, from_(addition_data))
#        if not fetch_(AUTO_GENERATE, from_(addition_data)):
#            self.driver.find(AUTO_GENERATE_CB).click()
#            self.driver.find_text_box(SHORT_NAME_ENABLED_TB).enter_text(short_name)
#        self.driver.find_text_box(LOCATION_TB).enter_text(
#            fetch_(LOCATION, from_(addition_data)))
#        self.driver.find_text_box(GEO_CODE_TB).enter_text(
#            fetch_(GPS, from_(addition_data)))
#        self.driver.find_text_box(DESCRIPTION_TB).enter_text(
#            fetch_(DESCRIPTION, from_(addition_data)))
#        self.driver.find_text_box(MOBILE_NUMBER_TB).enter_text(
#            fetch_(MOBILE_NUMBER, from_(addition_data)))
#        self.driver.find(ADD_BTN).click()
#        return fetch_(ERROR_MSG, from_(addition_data))

    def submit_subject(self):
        self.driver.find(SUBMIT_BTN).click()
        time.sleep(2)

    def get_error_message(self):
        """
        Function to fetch the error messages from error label of the add subject page

        Return error message
        """
        error_message = ""
        locators = self.driver.find_elements_(ERROR_MESSAGE_LABEL)
        if locators:
            for locator in locators:
                error_message = error_message + locator.text
        else:
            error = self.driver.find(ERROR_MESSAGE_BOX)
            error_message = error.text

        return str(error_message.replace("\n", " "))

    def get_flash_message(self):
        """
        Function to fetch the flash message from flash label of the add subject page

        Return message
        """
        comm_utils = CommonUtilities(self.driver)
        comm_utils.wait_for_element(5, FLASH_MESSAGE_LABEL)
        return self.driver.find(FLASH_MESSAGE_LABEL).text

    def get_selected_subject(self):
        """
        Function to fetch the selected subject from the drop down

        Return message
        """
        return self.driver.find_drop_down(ENTITY_TYPE_DD).get_selected()

    def get_title(self):
        return self.driver.get_title()

    def get_section_title(self):
        return self.driver.find(SECTION_TITLE).text

    def get_subject_type(self):
        return self.driver.find(SUBJECT_TYPE).text

    def go_back_to_project_list(self):
        self.driver.find(BACK_TO_PROJECT_LINK).click()

    def navigate_to_smart_phone_instruction(self):
        self.driver.find(SMARTPHONE_NAV).click()
        return SmartPhoneInstructionPage(self.driver)

    def get_cancel_url(self):
        return self.driver.find(CANCEL_LINK).get_attribute("href")