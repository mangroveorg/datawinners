from pages.page import Page
from pages.smartphoneinstructionpage.smart_phone_instruction_locator import SMART_PHONE_INSTRUCTION
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_locator import CLOSE_PREVIEW
from pages.websubmissionpage.web_submission_locator import WEB_NAVIGATION


class SmartPhoneInstructionPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_smart_phone_instruction(self):
        return self.driver.find(SMART_PHONE_INSTRUCTION)

    def navigate_to_project_list(self):
        self.driver.find(WEB_NAVIGATION).click()

    def close_preview(self):
        return self.driver.find(CLOSE_PREVIEW).click()
