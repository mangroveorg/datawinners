from framework.exception import CouldNotLocateElementException
from framework.utils.common_utils import by_css, by_id
from pages.page import Page


class QuestionnaireModifiedDialog(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def cancel(self):
        self.driver.find(by_id("cancel_dialog")).click()

    def save_changes(self):
        self.driver.find(by_id("save_changes")).click()

    def ignore_changes(self):
        return self.driver.find(by_id("ignore_changes")).click()

    def is_visible(self):
        try:
            return self.driver.find(by_id("ui-dialog-title-cancel_questionnaire_warning_message")).is_displayed()
        except CouldNotLocateElementException:
            return False