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
        return self.driver.find_elements_(by_css(".question-label"))[index].text

    def submit(self):
        self.driver.find_visible_element(by_id('validate-form')).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.success-message-box'), True)
        self.driver.wait_for_page_load()
        return self
