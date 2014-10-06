from pages.AutomaticReplySmsPage.automatic_reply_sms_page import AutomaticReplySmsPage
from pages.broadcastSMSpage.broadcast_sms_locator import *
from pages.page import Page

class BroadcastSmsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def write_sms_content(self, sms_data):
        self.driver.find_text_box(SMS_CONTENT_TB).enter_text(sms_data)

    def click_send(self):
         self.driver.find(SEND_BROADCAST_SMS_BTN).click()

    def get_sms_content(self):
        return self.driver.find_text_box(SMS_CONTENT_TB).get_attribute("value")

    def choose_type_other_people(self, other_numbers=None):
        self.driver.find(SEND_TO_DDCL).click()
        self.driver.find(OTHER_PEOPLE_OPTION_DDCL).click()
        if other_numbers is not None:
            self.driver.find_text_box(SEND_TO_TB).enter_text(other_numbers)

    def is_other_people_help_text_visible(self):
        return self.driver.find(OTHER_PEOPLE_HELP_TEXT).is_displayed()

    def get_other_people_number_error(self):
        return self.driver.find(OTHER_PEOPLE_ERROR_TEXT_BY_CSS).text

    def is_warning_shown(self):
        return self.driver.find(by_id("more_people_warning")).is_displayed()

    def navigate_to_automatic_reply_sms_page(self):
        self.driver.find(REPLY_SMS_LINK).click()
        return AutomaticReplySmsPage(self.driver)

    def is_send_a_message_to_unregistered_present(self):
        self.driver.find(SEND_TO_DDCL).click()
        return self.driver.find(by_css("ul li a#Unregistered")).is_displayed()