# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.lightbox.light_box_page import LightBox
from pages.smstesterlightbox.sms_tester_light_box_locator import *
import time
from framework.utils.data_fetcher import *
from tests.smstesterlightboxtests.sms_tester_light_box_data import *
from selenium.common.exceptions import NoSuchElementException


class SMSTesterLightBoxPage(LightBox):
    def __init__(self, driver):
        LightBox.__init__(self, driver)

    def send_sms_with(self, sms_data):
        """
        Function to enter and send the data using sms player

        Args:
        sms_data is data to fill in the text field

        Return self
        """
        self.driver.find_text_box(SMS_TA).enter_text(fetch_(SMS, from_(sms_data)))
        self.driver.find(SEND_SMS_BTN).click()
        #self.driver.wait_until_modal_dismissed(5)
        time.sleep(3)
        return self

    def get_response_message(self):
        """
        Function to fetch the success/error response message from text area of the page

        Return success/error message
        """
        return self.driver.find_text_box(SMS_TA).get_attribute("value")

    def get_upgrade_instruction_present(self):
        return self.driver.is_element_present(UPGRADE_INSTRUCTION_BY_CSS)

    def hit_clear_message_link(self):
        self.driver.find(CLEAR_BTN_BY_ID).click()

    def reply_turned_off_text_present(self):
        try:
            self.driver.find_element(value = 'outgoing_sms_disabled_help_text')
            return True
        except NoSuchElementException:
            return False
