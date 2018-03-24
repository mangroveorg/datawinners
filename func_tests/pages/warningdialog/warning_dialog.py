from framework.utils.common_utils import by_css
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT

CANCEL_LINK = by_css('div.ui-dialog[style*="block"] > div.ui-dialog-content > div > a.no_button')
CONFIRM_LINK = by_css('div.ui-dialog[style*="block"] > div.ui-dialog-content > div > a.yes_button')
MESSAGE_LINK = by_css('div.ui-dialog[style*="block"] > div.ui-dialog-content > .warning_message')

class WarningDialog(Page):
    def __init__(self, driver, cancel_link=CANCEL_LINK, confirm_link=CONFIRM_LINK, message_link=MESSAGE_LINK):
        Page.__init__(self, driver)
        self.cancel_link = cancel_link
        self.confirm_link = confirm_link
        self.message_link = message_link

    def cancel(self):
        self.driver.create_screenshot("debug-ft-before-hitting-cancel-button")
        try:
            self.driver.find(self.cancel_link).click()
        except Exception as e:
            self.driver.create_screenshot("debug-ft-cancel-button-not-found")
            raise e

    def confirm(self):
        self.driver.find(self.confirm_link).click()

    def get_message(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, self.message_link, True)
        return self.driver.find(self.message_link).text