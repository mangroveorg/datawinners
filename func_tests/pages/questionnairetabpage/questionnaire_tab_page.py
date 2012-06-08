from framework.utils.common_utils import by_css
from pages.createprojectpage.create_project_locator import SMS_PREVIEW
from pages.page import Page
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_page import SmsQuestionnairePreviewPage

class QuestionnaireTabPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def sms_questionnaire_preview(self):
        self.driver.find(SMS_PREVIEW).click()
        return SmsQuestionnairePreviewPage(self.driver)