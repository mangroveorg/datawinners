# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re

from framework.utils.common_utils import CommonUtilities
from pages.allsubjectspage.add_subject_page import AddSubjectPage
from pages.allsubjectspage.all_subjects_locator import *
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from pages.page import Page
from testdata.test_data import url
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage


class AllSubjectTypePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_add_a_subject_page(self):
        """
        Function to navigate to add a subject page of the website

        Return create project page
         """
        self.driver.find(ADD_A_SUBJECT_LINK).click()
        return AddSubjectPage(self.driver)

    def check_subject_type_on_page(self, subject):
        """
        Function to check the subject type on the all subject page of the website

        Return true or false
         """
        commUtils = CommonUtilities(self.driver)
        if commUtils.is_element_present(by_xpath(SUBJECT_TYPE_LINK % subject)):
            return True
        else:
            return False

    def add_new_subject_type(self, new_type):
        self.driver.find(ADD_SUBJECT_TYPE_LINK).click()
        self.driver.find_text_box(NEW_SUBJECT_TYPE_TB).enter_text(new_type)
        self.driver.find(ADD_SUBJECT_TYPE_SUBMIT_BUTTON).click()

    def navigate_to_edit_registration_form(self, entity_type, close_warning=False):
        self.driver.go_to(url("/entity/subject/edit/%s/" % entity_type.lower()))
        if close_warning:
            self.driver.find(CONTINUE_EDITING_BUTTON).click()
        return CreateQuestionnairePage(self.driver)

    def click_checkall_checkbox_for_entity_type(self, entity_type):
        commUtils = CommonUtilities(self.driver)
        if commUtils.is_element_present(by_css(CHECKALL_CB % entity_type)):
            self.driver.find(by_css(CHECKALL_CB % entity_type)).click()
            return True
        return False

    def get_checked_subjects_for_entity_type(self, entity_type):
        return len(self.driver.find(by_css(SUBJECT_TABLE_TBODY % entity_type)).find_elements(by="css selector",
                                                                                             value="tr td:first-child input[checked]"))

    def get_number_of_subject_for_entity_type(self, entity_type):
        commUtils = CommonUtilities(self.driver)
        if commUtils.is_element_present(by_xpath(SUBJECTS_INFO % entity_type.capitalize())):
            info = self.driver.find(by_xpath(SUBJECTS_INFO % entity_type.capitalize())).text
            return int(re.match(r'\d+', info).group(), 10)
        else:
            return False

    def open_subjects_table_for_entity_type(self, entity_type):
        commUtils = CommonUtilities(self.driver)
        if commUtils.is_element_present(by_xpath(SUBJECT_TYPE_LINK % entity_type.capitalize())):
            self.driver.find(by_xpath(SUBJECT_TYPE_LINK % entity_type.capitalize())).click()
        else:
            return False

    def get_subject_type_number(self, subject_type):
        for i, type in enumerate(self.driver.find(ALL_SUBJECT_TYPES_CONTAINER).find_elements(by="css selector",
                                                                                             value="div.list_header span.header")):
            if type.text.lower() == subject_type.lower():
                return i + 1

        return -1

    def click_action_button_for(self, action=None):
        (self.driver.find_elements(by='xpath', value='//*[@id="action_button"]/div/button')[1]).click()
        self.driver.find_elements(by='css',value='.'+action)[0].click()

    def is_edit_enabled_for(self, subject_type):
        subject_number = self.get_subject_type_number(subject_type)
        edit_links = self.driver.find(ALL_SUBJECT_TYPES_CONTAINER).find_elements(by="xpath",
                                                                                 value="//a[@class='edit']/parent::li")
        css_class = edit_links[subject_number - 1].get_attribute("class")
        return css_class.find("disabled") < 0

    def is_none_selected_shown_for(self, subject_type):
        subject_number = self.get_subject_type_number(subject_type)
        return self.driver.find(by_id("none-selected%s" % str(subject_number))).is_displayed()

    def actions_menu_shown_for(self, subject_type):
        subject_number = self.get_subject_type_number(subject_type)
        return self.driver.find(by_id("action%s" % str(subject_number))).is_displayed()

    def select_a_subject_by_type_and_id(self, subject_type, uid):
        self.is_subject_present(subject_type, uid).click()

    def is_checkall_checked_for_entity_type(self, entity_type):
        return self.driver.find(by_css(CHECKALL_CB % entity_type)).get_attribute("checked") == "true"

    def message(self):
        return self.driver.find(by_css('ul.messages > li.success')).text

    def is_subject_present(self, subject_type, subject_short_code):
        try:
            return self.driver.find(by_xpath('//input[@value="%s"'%subject_short_code+']'))
        except:
            return None

    def select_subject_type(self, subject_type):
        self.driver.find_element_by_link_text(subject_type).click()
        return AllSubjectsListPage(self.driver)