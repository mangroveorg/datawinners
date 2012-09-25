from pages.page import Page
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_locator import QUESTIONNAIRE_PREVIEW, PROJECT_NAME, \
    INSTRUCTION, PREVIEW_STEPS, CLOSE_PREVIEW, QUESTION_BY_CSS_LOCATOR
from framework.utils.common_utils import by_css

class SmsQuestionnairePreviewPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def sms_questionnaire(self):
        return self.driver.find(QUESTIONNAIRE_PREVIEW)

    def get_project_name(self):
        return self.driver.find(PROJECT_NAME).text

    def get_sms_instruction(self):
        return self.driver.find(INSTRUCTION)

    def close_preview(self):
        return self.driver.find(CLOSE_PREVIEW).click()

    def sms_questionnaire_exist(self):
        return self.driver.is_element_present(QUESTIONNAIRE_PREVIEW)

    def has_preview_steps(self):
        return self.driver.is_element_present(PREVIEW_STEPS)

    def get_question_content(self, index):
        return self.driver.find(by_css(QUESTION_BY_CSS_LOCATOR % str(index))).text