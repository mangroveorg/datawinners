from framework.utils.common_utils import by_css
from pages.datasenderpage.data_sender_locator import SEND_IN_DATA_LINK, PROJECT_LIST
from pages.page import Page
from pages.websubmissionpage.web_submission_page import WebSubmissionPage


class DataSenderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def send_in_data(self):
        self.driver.find(SEND_IN_DATA_LINK).click()
        return WebSubmissionPage(self.driver)

    def get_project_list(self):
        return self.driver.find(PROJECT_LIST)
