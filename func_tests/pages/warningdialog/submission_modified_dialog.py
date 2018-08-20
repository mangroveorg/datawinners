from framework.utils.common_utils import by_id
from pages.page import Page


class SubmissionModifiedDialog(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def cancel(self):
        self.driver.find(by_id("cancel_submission_warning_message_dialog_section"))\
            .find_element_by_id("cancel_dialog").click()

    def save_changes(self):
        self.driver.find(by_id("cancel_submission_warning_message_dialog_section"))\
            .find_element_by_id("save_changes").click()

    def ignore_changes(self):
        return self.driver.find(by_id("cancel_submission_warning_message_dialog_section"))\
            .find_element_by_id("ignore_changes").click()
