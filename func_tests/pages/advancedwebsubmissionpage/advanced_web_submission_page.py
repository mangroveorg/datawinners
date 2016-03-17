from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from framework.utils.common_utils import by_id, by_css
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from tests.testsettings import UI_TEST_TIMEOUT


class AdvancedWebSubmissionPage(WebSubmissionPage):

    def __init__(self, driver):
        WebSubmissionPage.__init__(self, driver)

    def update_text_input(self, locator, text):
        self.driver.find_visible_element(locator).send_keys(text)
        return self

    def get_label(self, index):
        return self._get_question(index).find_element(by=By.CSS_SELECTOR, value=".question-label").text

    def get_hint(self, index):
        return self._get_question(index).find_element(by=By.CSS_SELECTOR, value=".or-hint").text

    def get_constraint_msg(self, index):
        return self._get_question(index).find_element(by=By.CSS_SELECTOR, value=".or-constraint-msg").text

    def text_area_present(self, index):
        try:
            return self._get_question(index).find_element(by=By.CSS_SELECTOR, value="textarea")
        except NoSuchElementException:
            return False

    def input_present(self, index):
        try:
            return self._get_question(index).find_element(by=By.CSS_SELECTOR, value="input")
        except NoSuchElementException:
            return False

    def set_input(self, index, value):
        input_element = self._get_question(index).find_element(by=By.CSS_SELECTOR, value="input")
        input_element.send_keys(value)
        input_element.send_keys(Keys.TAB)

    def submit(self):
        self.driver.find_visible_element(by_id('validate-form')).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.success-message-box'), True)
        self.driver.wait_for_page_load()
        return self

    def _get_question(self, index):
        return self.driver.find_elements_(by_css(".question"))[index]
