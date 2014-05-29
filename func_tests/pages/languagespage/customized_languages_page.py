from framework.utils.common_utils import by_id, by_css
from framework.utils.drop_down_web_element import DropDown
from framework.utils.text_box_web_element import TextBox
from pages.languagespage.customized_language_locator import LANGUAGE_DROP_DOWN_LOCATOR, LANGUAGE_SAVE_BUTTON_LOCATOR, NEW_LANGUAGE_INPUT_BOX, ADD_NEW_LANG_CONFIRM_BUTTON
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class CustomizedLanguagePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.language_drop_down = DropDown(self.driver.find(LANGUAGE_DROP_DOWN_LOCATOR))


    def get_selected_language(self):
        return self.language_drop_down.get_selected_option_text()

    def set_custom_message_for(self, msg_locator, message):
        custom_message_text_box = TextBox(self.driver.find(msg_locator))
        custom_message_text_box.enter_text(message)
        self.save_changes()

    def save_changes(self):
        self.driver.find(LANGUAGE_SAVE_BUTTON_LOCATOR).click()

    def get_success_message(self):
        success_message = self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css(".success-message-box"),want_visible=True)
        return self.driver.execute_script("return arguments[0].innerHTML", success_message)

    def select_language(self,language_text, wait_for_load = False):
        self.language_drop_down.set_selected_by_text(language_text)
        if wait_for_load:
            self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".blockUI"))


    def get_custom_message_for(self,msg_locator):
        return self.driver.find(msg_locator).get_attribute("value")

    def get_all_messages(self):
        return [r.get_attribute('value') for r in self.driver.find_elements_(by_css("#language_customized_messages textarea"))]

    def set_message_boxes(self, default_en_messages):
        for (index, e) in enumerate(self.driver.find_elements_(by_css("#language_customized_messages textarea"))):
            e.clear()
            e.send_keys(default_en_messages[index])

    def add_new_language(self, language_name):
        self.language_drop_down.set_selected_by_text(self.language_drop_down.get_options()[-1])
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('.ui-dialog'))
        self.driver.find_text_box(NEW_LANGUAGE_INPUT_BOX).enter_text(language_name)
        self.driver.find(ADD_NEW_LANG_CONFIRM_BUTTON).click()
