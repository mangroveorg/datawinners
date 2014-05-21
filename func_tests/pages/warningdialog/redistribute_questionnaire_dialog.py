from framework.exception import CouldNotLocateElementException
from framework.utils.common_utils import by_css, by_id
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT

class RedistributeQuestionnaireDialog(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def confirm(self):
        self.driver.find(by_css("#inform_datasender_about_changes .yes_button")).click()

    def get_message(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("inform_datasender_about_changes"), True)
        return self.driver.find(by_id("inform_datasender_about_changes"))\
            .find_element_by_class_name("warning_message").text