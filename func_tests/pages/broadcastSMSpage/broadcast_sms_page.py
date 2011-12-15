from pages.broadcastSMSpage.broadcast_sms_locator import SMS_CONTENT_TB, SEND_BROADCAST_SMS_BTN
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