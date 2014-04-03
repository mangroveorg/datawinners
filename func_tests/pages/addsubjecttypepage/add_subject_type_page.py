# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from framework.utils.common_utils import generateId
from pages.allsubjectspage.all_subject_type_page import AllSubjectTypePage
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from pages.page import Page
from framework.utils.data_fetcher import from_, fetch_
from pages.addsubjecttypepage.add_subject_type_locator import *
from tests.subjecttypetests.add_subject_type_data import *
from time import sleep


class AddSubjectTypePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def successfully_add_entity_type_with(self, entity_type):
        """
        Function to enter randomly generated entity type in the text box and click on the Add button
         .
        Args:
        'entity_data' is entity name

        Return self
        """
        self.driver.find_text_box(NEW_SUBJECT_TB).enter_text(entity_type)
        self.driver.find(ADD_BTN).click()
        self.driver.wait_until_element_is_not_present(5, by_css("#type_message .ajax_loader"))
        return AllSubjectTypePage(self.driver)

    def add_entity_type_with(self, entity_type, wait=True):
        """
        Function to enter entity type in the text box and click on the Add button
         .
        Args:
        'entity_data' is entity name

        Return self
        """
        sleep(1)
        self.driver.find_text_box(NEW_SUBJECT_TB).enter_text(entity_type)
        self.driver.find(ADD_BTN).click()
        if wait:
            self.driver.wait_until_element_is_not_present(5, by_css("#type_message .ajax_loader_small"))
        return self

    def get_error_message(self):
        """
        Function to fetch the error message from error label of the Add a  Subject Type
        page

        Return error message
        """
        return self.driver.find(ERROR_MESSAGE_LABEL).text

    def click_on_accordian_link(self):
        """
        Function to open/close the accordian of the add a subject type

        Return self
        """
        self.driver.find(ADD_NEW_SUBJECT_TYPE_LINK).click()
        return self

    def click_all_subject_type(self, check=True):
        checkbox = self.driver.find(CHECK_ALL_SUBJECT_TYPE_LOCATOR)
        if (checkbox.get_attribute("checked") != "true" and check) or \
                (checkbox.get_attribute("checked") == "true" and not check):
            checkbox.click()
        return self

    def click_action_button(self):
        self.driver.find(ALL_SUBJECT_TYPE_ACTION_SELECT).click()
        return self

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def get_message(self):
        if self.driver.is_element_present(MESSAGES_CONTAINER):
            return self.driver.find(MESSAGES_CONTAINER).text
        return False

    def click_subject_type(self, subject_type):
        self.driver.find(by_xpath("//input[@value='%s']"%subject_type)).click()
        return self

    def select_subject_type(self, subject_type):
        self.driver.find_element_by_link_text(subject_type.capitalize()).click()
        return AllSubjectsListPage(self.driver)

    def select_delete_action(self, confirm=False, cancel=False):
        action_to_be_performed = DELETE
        self.perform_user_action(action_to_be_performed)
        if confirm:
            self.confirm_delete()
        if cancel:
            self.cancel_delete()

    def confirm_delete(self):
        self.driver.find(CONFIRM_DELETE_BUTTON).click()

    def cancel_delete(self):
        self.driver.find(CANCEL_DELETE_BUTTON).click()

    def perform_user_action(self, action_to_be_performed):
        self.click_action_button()
        option = self.driver.find_visible_element(by_id(action_to_be_performed))
        option.click()
