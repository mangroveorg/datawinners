from pages.page import Page
from pages.warningdialog.warning_dialog_locator import CANCEL_LINK, CONFIRM_LINK, MESSAGE_LINK


class WarningDialog(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def cancel(self):
        self.driver.find(CANCEL_LINK).click()

    def confirm(self):
        self.driver.find(CONFIRM_LINK).click()

    def get_message(self):
        return self.driver.find(MESSAGE_LINK).text
