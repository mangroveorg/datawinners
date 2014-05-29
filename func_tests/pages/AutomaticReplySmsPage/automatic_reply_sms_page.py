import time
from framework.utils.drop_down_web_element import DropDown
from pages.AutomaticReplySmsPage.automatic_reply_sms_page_locators import AVAILABLE_LANGUAGES_DROPDOWN_ID, NEW_LANGUAGE_OPTION_SELECTOR, PROJECT_LANGUAGE_PAGE_SAVE_BUTTON, PROJECT_LANGUAGE_PAGE_SUCCESS_MESSAGE_BOX
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class AutomaticReplySmsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.language_drop_down = DropDown(self.driver.find(AVAILABLE_LANGUAGES_DROPDOWN_ID))


    def choose_automatic_reply_language(self, language):
        #self.language_drop_down.click()
        if language == 'new':
            #time.sleep(3)
            #self.driver.find(NEW_LANGUAGE_OPTION_SELECTOR).click()
            self.language_drop_down.set_selected('new_lang')
            self.driver.create_screenshot('automatic_sms_reply_error.png')
            self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, 'Languages')
            return CustomizedLanguagePage(self.driver)
        self.language_drop_down.set_selected_by_text(language)

    def save_changes(self):
        self.driver.find(PROJECT_LANGUAGE_PAGE_SAVE_BUTTON).click()

    def get_success_message(self):
        return self.driver.find(PROJECT_LANGUAGE_PAGE_SUCCESS_MESSAGE_BOX).text