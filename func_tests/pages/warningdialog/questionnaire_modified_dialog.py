from framework.exception import CouldNotLocateElementException
from framework.utils.common_utils import by_css, by_id
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class QuestionnaireModifiedDialog(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def cancel(self):
        self.driver.find(by_id("cancel_questionnaire_warning_message_dialog_section"))\
            .find_element_by_id("cancel_dialog").click()

    def save_changes(self):
        self.driver.find(by_id("cancel_questionnaire_warning_message_dialog_section"))\
            .find_element_by_id("save_changes").click()

    def ignore_changes(self):
        return self.driver.find(by_id("cancel_questionnaire_warning_message_dialog_section"))\
            .find_element_by_id("ignore_changes").click()

    def is_visible(self):
        try:
            id = by_id("cancel_questionnaire_warning_message_dialog_section")
            self.driver.wait_for_element(UI_TEST_TIMEOUT, id, True)
            return self.driver.find(id).is_displayed()
        except CouldNotLocateElementException:
            return False

    def is_hidden(self):
        try:
            id = by_id("cancel_questionnaire_warning_message_dialog_section")
            self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, id)
            return self.driver.find(id).is_displayed() == False
        except CouldNotLocateElementException:
            return True