from pages.previewnavigationpage.preview_navigation_locator import SMS_PREVIEW, WEB_PREVIEW, SMART_PHONE_PREVIEW
from pages.smartphoneinstructionpage.smart_phone_instruction_page import SmartPhoneInstructionPage
from pages.smsquestionnairepreviewpage.sms_questionnaire_preview_page import SmsQuestionnairePreviewPage
from pages.webquestionnairepreivewpage.web_questionnaire_preivew_page import WebQuestionnairePreviewPage
from pages.page import Page

class PreviewNavigationPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
    
    def sms_questionnaire_preview(self):
        self.driver.find(SMS_PREVIEW).click()
        return SmsQuestionnairePreviewPage(self.driver)

    def web_questionnaire_preview(self):
        self.driver.find(WEB_PREVIEW).click()
        return WebQuestionnairePreviewPage(self.driver)

    def smart_phone_preview(self):
        self.driver.find(SMART_PHONE_PREVIEW).click()
        return SmartPhoneInstructionPage(self.driver)