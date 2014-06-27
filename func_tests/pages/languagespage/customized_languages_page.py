from selenium.webdriver.support.wait import WebDriverWait

from framework.utils.common_utils import by_css, by_id
from framework.utils.drop_down_web_element import DropDown
from framework.utils.text_box_web_element import TextBox
from pages.languagespage.account_wide_reply_sms_page import AccountWideSmsReplyPage
from pages.languagespage.customized_language_locator import LANGUAGE_DROP_DOWN_LOCATOR, LANGUAGE_SAVE_BUTTON_LOCATOR, NEW_LANGUAGE_INPUT_BOX, ADD_NEW_LANG_CONFIRM_BUTTON, CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR, ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR, \
    REVERT_TO_ORIGINAL_LINK, CANCEL_CHANGES_LOCATOR
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class CustomizedLanguagePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.language_drop_down = DropDown(self.driver.find(LANGUAGE_DROP_DOWN_LOCATOR))

    def get_selected_language(self):
        return self.language_drop_down.get_selected_option_text()

    def update_message_for_selector(self, msg_locator, message):
        custom_message_text_box = self.driver.find(msg_locator)
        self.update_custom_message(message, custom_message_text_box)

    def remove_appended_message_for_selector(self, locator, message):
        custom_message_text_box = self.driver.find(locator)
        self.driver.execute_script("$(arguments[0]).html(_.str.rtrim($(arguments[0]).html(), arguments[1])); $(arguments[0]).trigger( 'blur' );", custom_message_text_box, message)
        self.save_changes()

    def update_custom_message(self, message, message_box):
        self.driver.execute_script("$(arguments[0]).html($(arguments[0]).html() + arguments[1]);", message_box, message)
        # hack to update ko viewmodel
        self.driver.execute_script("$(arguments[0]).trigger( 'blur' );", message_box)

    def click_revert_changes_button(self):
        dont_save_button = self.driver.find_visible_element(by_css(".no_button"))
        dont_save_button.click()
        self.driver.wait_until_web_element_is_not_present(UI_TEST_TIMEOUT, dont_save_button)

    def click_save_changes_button(self):
        self.driver.find_visible_element(by_css(".yes_button")).click()
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".ui-dialog-titlebar"))
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".blockPage"))

    def clear_custom_message(self, message_box_locator):
        message_box = self.driver.find(message_box_locator)
        message_box.clear()
        # hack to update ko viewmodel
        self.driver.execute_script("$(arguments[0]).trigger( 'blur' );", message_box)

    def append_custom_message_for(self, msg_locator, message):
        message_box = self.driver.wait_for_element(UI_TEST_TIMEOUT, msg_locator, want_visible=True)
        self.update_custom_message(message, message_box)

    def save_changes(self):
        self.driver.find(LANGUAGE_SAVE_BUTTON_LOCATOR).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".success-message-box"), True)

    def get_success_message(self):
        success_message = self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".success-message-box"),want_visible=True)
        return self.driver.execute_script("return arguments[0].innerHTML", success_message)

    def wait_till_success_message_box_disappears(self):
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".success-message-box"))

    def select_language(self,language_text, wait_for_load=False):
        self.language_drop_down.set_selected_by_text(language_text)
        if wait_for_load:
            self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".blockPage"))
        self.wait_for_reply_messages_to_load()

    def wait_for_reply_messages_to_load(self):
        #waiting for the last custom message to be populated
        WebDriverWait(self.driver, UI_TEST_TIMEOUT).until(lambda driver:  driver.execute_script("return $('#custom_message4').text().length > 0"))

    def get_custom_message_for(self, msg_locator):
        msg_box = self.driver.find(msg_locator)
        return self.driver.execute_script("return $(arguments[0]).html()", msg_box)

    def get_all_customized_reply_messages(self):
        return [self.driver.execute_script("return $(arguments[0]).TextNTags('getText')", r) for r in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR)]

    def set_message_boxes(self, default_en_messages,locator=CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR):
        for (index, e) in enumerate(self.driver.find_elements_(locator)):
            e.clear()
            e.send_keys(default_en_messages[index])

    def revert_customized_messages_to_default(self):
        return [self.driver.execute_script("$(arguments[0]).html(_.str.rtrim($(arguments[0]).html(),'new message')); $(arguments[0]).trigger( 'blur' );", r) for r in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR)]

    def save_new_language(self, language_name):
        self.driver.find_text_box(NEW_LANGUAGE_INPUT_BOX).enter_text(language_name)
        self.driver.find(ADD_NEW_LANG_CONFIRM_BUTTON).click()

    def add_new_language(self, language_name):
        self.select_add_new_language_option()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.ui-dialog'))
        self.save_new_language(language_name)

    def select_add_new_language_option(self):
        self.driver.find(by_css('#add_language_link')).click()

    def navigate_to_account_message_Tab(self):
        self.driver.find(by_id('account_wide_sms_link')).click()
        return AccountWideSmsReplyPage(self.driver)

    def revert_to_original(self):
        [r.click() for r in self.driver.find_elements_(REVERT_TO_ORIGINAL_LINK)]

    def cancel_changes(self):
        self.driver.find(CANCEL_CHANGES_LOCATOR).click()

    def keep_changes(self):
        self.driver.find_visible_element(by_id("keep_changes")).click()

    def revert_changes(self):
        self.driver.find_visible_element(by_id("revert_changes")).click()
