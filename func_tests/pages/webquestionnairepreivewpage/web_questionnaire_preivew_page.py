from pages.page import Page
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_locator import QUESTIONNAIRE_PREVIEW, INSTRUCTION, CLOSE_PREVIEW


class WebQuestionnairePreviewPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def web_questionnaire(self):
        return self.driver.find(QUESTIONNAIRE_PREVIEW)

    def get_web_instruction(self):
        return self.driver.find(INSTRUCTION)

    def close_preview(self):
        return self.driver.find(CLOSE_PREVIEW).click()
