from pages.page import Page
from pages.warningdialog.warning_dialog_locator import CANCEL_LINK, CONFIRM_LINK, MESSAGE_LINK


class WarningDialog(Page):
    def __init__(self, driver, cancel_link=CANCEL_LINK, confirm_link=CONFIRM_LINK, message_link=MESSAGE_LINK):
        Page.__init__(self, driver)
        self.cancel_link = cancel_link
        self.confirm_link = confirm_link
        self.message_link = message_link

    def cancel(self):
        self.driver.find(self.cancel_link).click()

    def confirm(self):
        self.driver.find(self.confirm_link).click()

    def get_message(self):
        self.driver.wait_for_element(5, self.message_link)
        return self.driver.find(self.message_link).text