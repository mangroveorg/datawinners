import time
from selenium.common.exceptions import NoSuchElementException
from framework.utils.common_utils import by_css, by_id
from framework.utils.drop_down_web_element import DropDown
from pages.AutomaticReplySmsPage.automatic_reply_sms_page_locators import AVAILABLE_LANGUAGES_DROPDOWN_ID, PROJECT_LANGUAGE_PAGE_SAVE_BUTTON, PROJECT_LANGUAGE_PAGE_SUCCESS_MESSAGE_BOX, NEW_LANGUAGE_CREATE_SELECTOR
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.page import Page
from pages.projectoverviewpage.project_overview_locator import TEST_QUESTIONNAIRE_LINK
from pages.smstesterlightbox.sms_tester_light_box_page import SMSTesterLightBoxPage
from tests.testsettings import UI_TEST_TIMEOUT


class AutomaticReplySmsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.language_drop_down = DropDown(self.driver.find(AVAILABLE_LANGUAGES_DROPDOWN_ID))


    def choose_automatic_reply_language(self, language):
        if language == 'new':
            self.driver.find(NEW_LANGUAGE_CREATE_SELECTOR).click()
            self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, 'Languages')
            return CustomizedLanguagePage(self.driver)
        self.language_drop_down.set_selected_by_text(language)

    def save_changes(self):
        self.driver.find(PROJECT_LANGUAGE_PAGE_SAVE_BUTTON).click()

    def get_success_message(self):
        return self.driver.find(PROJECT_LANGUAGE_PAGE_SUCCESS_MESSAGE_BOX).text

    def turn_off_reply_messages(self):
        try:
            on_off_switch = self.driver.find_visible_element(by_css('.onoffswitch-checked'))
            on_off_switch.click()
        except Exception:
            pass
        self.save_changes()

    def turn_on_reply_messages(self):
        try:
            self.driver.find_visible_element(by_css('.onoffswitch-checked'))
        except Exception:
            self.driver.find_visible_element(by_css('.onoffswitch')).click()
        self.save_changes()

    def is_language_selection_enabled(self):
        return self.driver.find(AVAILABLE_LANGUAGES_DROPDOWN_ID).is_enabled()

    def open_sms_tester_light_box(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT,TEST_QUESTIONNAIRE_LINK,True)
        self.driver.find(TEST_QUESTIONNAIRE_LINK).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.mobile'), True)
        return SMSTesterLightBoxPage(self.driver)
