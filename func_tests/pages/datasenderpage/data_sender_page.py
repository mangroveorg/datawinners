from pages.allsubjectspage.add_subject_page import AddSubjectPage
from pages.datasenderpage.data_sender_locator import SEND_IN_DATA_LINK, PROJECT_LIST, REGISTER_SUBJECT, SMARTPHONE_NAV
from pages.page import Page
from pages.smartphoneinstructionpage.smart_phone_instruction_page import SmartPhoneInstructionPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage


class DataSenderPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def send_in_data(self):
        self.driver.find(SEND_IN_DATA_LINK).click()
        return WebSubmissionPage(self.driver)

    def get_project_list(self):
        return self.driver.find(PROJECT_LIST)

    def register_subject(self):
        self.driver.find(REGISTER_SUBJECT).click()
        return AddSubjectPage(self.driver)

    def navigate_to_smart_phone_instruction(self):
        self.driver.find(SMARTPHONE_NAV).click()
        return SmartPhoneInstructionPage(self.driver)