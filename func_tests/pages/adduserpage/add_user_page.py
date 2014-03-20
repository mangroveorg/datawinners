# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from pages.page import Page
from framework.utils.common_utils import by_css
from pages.adddatasenderspage.add_data_senders_locator import FLASH_MESSAGE_LABEL
from tests.testsettings import UI_TEST_TIMEOUT


class AddUserPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def add_user_with(self, user_data):
        for key,value in user_data.items():
            self.driver.find_text_box(by_css("input[name=%s]" % key)).enter_text(value)
        self.driver.find(by_css("input[type=submit]")).click()

    def get_success_message(self):
        locator = self.driver.wait_for_element(UI_TEST_TIMEOUT*2, FLASH_MESSAGE_LABEL)
        return locator.text