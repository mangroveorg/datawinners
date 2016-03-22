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

    def constraint_msg_visible(self, index):
        return self._get_question(index).find_element(by=By.CSS_SELECTOR, value=".or-constraint-msg").is_displayed()

    def get_constraint_msg(self, index):
        return self._get_question(index).find_element(by=By.CSS_SELECTOR, value=".or-constraint-msg").text

    def text_area_present(self, index):
        try:
            return self._get_question(index).find_element(by=By.CSS_SELECTOR, value="textarea")
        except NoSuchElementException:
            return False

    def input_present(self, index):
        try:
            return self._get_input(index)
        except NoSuchElementException:
            return False

    def input_with_name_present(self, name):
        return self._get_input_with_name(name)

    def set_input(self, index, value):
        input_element = self._get_input(index)
        existing = 0 if not input_element.get_attribute("value") else int(input_element.get_attribute("value"))
        key = Keys.UP if value > existing else Keys.DOWN
        for index in range(abs(value - existing)):
            input_element.send_keys(key)
        input_element.send_keys(Keys.TAB)

    def get_input_name(self, index):
        return self._get_input(index).get_attribute("name")

    def get_input_value(self, index):
        return self._get_input(index).get_attribute("value")

    def submit(self):
        self.driver.find_visible_element(by_id('validate-form')).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.success-message-box'), True)
        self.driver.wait_for_page_load()
        return self

    def question_count(self):
        return len(self._get_questions())

    def _get_input(self, index):
        return self._get_question(index).find_element(by=By.CSS_SELECTOR, value="input")

    def _get_input_with_name(self, name):
        for qn in self._get_questions():
            try:
                elem = qn.find_element(by=By.CSS_SELECTOR, value="input[name*='" + name + "']")
                if elem:
                    return elem
            except NoSuchElementException:
                continue
        return False

    def _get_question(self, index):
        return self._get_questions()[index]

    def _get_questions(self):
        return self.driver.find_elements_(by_css(".question"))
