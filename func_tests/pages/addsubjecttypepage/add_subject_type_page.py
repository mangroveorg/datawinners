# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from framework.utils.common_utils import generateId
from pages.allsubjectspage.all_subjects_page import AllSubjectsPage
from pages.page import Page
from framework.utils.data_fetcher import from_, fetch_
from pages.addsubjecttypepage.add_subject_type_locator import *
from tests.addsubjecttypetests.add_subject_type_data import *


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
        return AllSubjectsPage(self.driver)

    def add_entity_type_with(self, entity_type, wait=True):
        """
        Function to enter entity type in the text box and click on the Add button
         .
        Args:
        'entity_data' is entity name

        Return self
        """
        self.driver.find_text_box(NEW_SUBJECT_TB).enter_text(entity_type)
        self.driver.find(ADD_BTN).click()
        if wait:
            self.driver.wait_until_element_is_not_present(5, by_css("#type_message .ajax_loader"))
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
