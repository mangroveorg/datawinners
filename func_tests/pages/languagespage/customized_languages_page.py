from framework.utils.common_utils import by_id, by_css
from framework.utils.drop_down_web_element import DropDown
from framework.utils.text_box_web_element import TextBox
from pages.languagespage.customized_language_locator import LANGUAGE_DROP_DOWN_LOCATOR, LANGUAGE_SAVE_BUTTON_LOCATOR, NEW_LANGUAGE_INPUT_BOX, ADD_NEW_LANG_CONFIRM_BUTTON, CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR, ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class CustomizedLanguagePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.language_drop_down = DropDown(self.driver.find(LANGUAGE_DROP_DOWN_LOCATOR))


    def get_selected_language(self):
        return self.language_drop_down.get_selected_option_text()

    def set_custom_message_for(self, msg_locator, message):
        custom_message_text_box = self.driver.find(msg_locator)
        custom_message_text_box.send_keys(message)
        # hack to update ko viewmodel
        self.driver.execute_script("$(arguments[0]).trigger('keydown');$(arguments[0]).trigger('blur');", custom_message_text_box)

    def update_custom_message(self, message, message_box):
        self.driver.execute_script("$(arguments[0]).html($(arguments[0]).html() + arguments[1]);", message_box, message)
        # hack to update ko viewmodel
        self.driver.execute_script("$(arguments[0]).trigger( 'blur' );", message_box)

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
            self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".blockUI"))


    def get_custom_message_for(self, msg_locator):
        msg_box = self.driver.find(msg_locator)
        return self.driver.execute_script("return $(arguments[0]).html()", msg_box)

    def get_all_customized_reply_messages(self):
        return [self.driver.execute_script("return $(arguments[0]).TextNTags('getText')",r) for r in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR)]

    def get_all_account_wide_messages(self):
        return [self.driver.execute_script("return $(arguments[0]).TextNTags('getText')",r) for r in self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]

    def set_message_boxes(self, default_en_messages,locator=CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR):
        for (index, e) in enumerate(self.driver.find_elements_(locator)):
            e.clear()
            e.send_keys(default_en_messages[index])

    def revert_account_messages_to_default(self):
        return [self.driver.execute_script("$(arguments[0]).html(_.str.rtrim($(arguments[0]).html(),'new message')); $(arguments[0]).trigger( 'blur' );", r) for r in self.driver.find_elements_(ACCOUNT_WIDE_MESSAGE_TEXTBOXES_LOCATOR)]

    def revert_customized_messages_to_default(self):
        return [self.driver.execute_script("$(arguments[0]).html(_.str.rtrim($(arguments[0]).html(),'new message')); $(arguments[0]).trigger( 'blur' );", r) for r in self.driver.find_elements_(CUSTOMIZED_MESSAGE_TEXTBOXES_LOCATOR)]

    def add_new_language(self, language_name):
        self.language_drop_down.set_selected_by_text(self.language_drop_down.get_options()[-1])
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.ui-dialog'))
        self.driver.find_text_box(NEW_LANGUAGE_INPUT_BOX).enter_text(language_name)
        self.driver.find(ADD_NEW_LANG_CONFIRM_BUTTON).click()
