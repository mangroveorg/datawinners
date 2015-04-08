from pages.adddatasenderspage.add_data_senders_locator import *
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class AddGroupPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def enter_group_name(self, group_name):
        return self.driver.find_text_box(ADD_GROUP_DIALOG).enter_text(group_name)

    def click_on_add_group_button(self):
        element = self.driver.find(ADD_GROUP_BUTTON)
        return element.click()

    def wait_for_table_data_to_load(self):
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_id("datasender_table_processing"))

    def wait_for_table_to_load(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id("datasender_table"), True)
        self.wait_for_table_data_to_load()

    def add_or_remove_contact_to_group(self, group_name):
        self.driver.wait_for_element(UI_TEST_TIMEOUT,  by_xpath(ADD_CONTACT_TO_GROUP % group_name), True)
        self.driver.find(by_xpath(ADD_CONTACT_TO_GROUP % group_name)).click()

    def remove_contact_from_group(self, group_name):
        self.driver.wait_for_element(UI_TEST_TIMEOUT,  by_xpath(ADD_CONTACT_TO_GROUP % group_name), True)
        self.driver.find(by_xpath(ADD_CONTACT_TO_GROUP % group_name)).click()

    def click_on_contact_to_group_button(self):
        self.driver.find(by_css('#add_contacts_to_group')).click()

    def enter_new_group_name(self, new_group_name):
        group_name_tb = self.driver.find_text_box(RENAME_GROUP_DIALOG)
        return group_name_tb.enter_text(new_group_name)

    def click_on_rename_group(self):
        self.driver.find(RENAME_GROUP_BUTTON).click()
        self.wait_for_table_to_load()

    def click_on_confirm_delete_group(self):
        self.driver.find(DELETE_GROUP_BUTTON).click()
        self.wait_for_table_to_load()

class AddContactPage(AddGroupPage):

    def __init__(self, driver):
        AddGroupPage.__init__(self, driver)