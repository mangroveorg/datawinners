from selenium.webdriver.support.wait import WebDriverWait
from pages.allsubjectspage.add_subject_page import AddSubjectPage
from pages.page import Page
from pages.projectsubjectspage.project_subjects_locator import *
from framework.utils.common_utils import by_css
from tests.testsettings import UI_TEST_TIMEOUT


class ProjectSubjectsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def click_edit_form_link_and_continue(self):
        self.driver.find(EDIT_FORM_LINK).click()
        self.driver.wait_for_element(5, EDIT_CONTINUE_LINK)
        self.driver.find(EDIT_CONTINUE_LINK).click()

    def click_add_question_link(self):
        self.driver.find(ADD_QUESTION_LINK).click()

    def get_selected_question_label(self):
        return self.driver.find(SELECTED_QUESTION_LABEL).text

    def click_submit_button(self):
        self.driver.find(SUBMIT_BTN).click()

    def is_success_message_tip_show(self):
        self.driver.wait_for_element(5, SUCCESS_MESSAGE_TIP)
        return self.driver.find(SUCCESS_MESSAGE_TIP) is not None

    def is_question_type_enabled(self):
        return self.driver.find(TYPE_CB).is_enabled()

    def click_action_button(self):
        self.driver.find(ACTION_DROP_DOWN).click()

    def is_edit_action_disabled(self):
        return self.driver.find(by_css("#action a.edit")).get_attribute("disabled") == "true"

    def is_edit_action_displayed(self):
        # WebDriverWait(self.driver, 1).until(lambda driver: self.driver.find(by_css("#action a.edit")).is_displayed())
        return self.driver.find(by_css("#action a.edit")).is_displayed()

    def is_delete_action_displayed(self):
        return self.driver.find(by_css("#action a.delete")).is_displayed()

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def is_empty_actions_menu_shown(self):
        return self.driver.find(EMPTY_ACTION_MENU).is_displayed()

    def navigate_to_my_subjects_list_tab(self):
        self.driver.find(MY_SUBJECTS_TAB_LINK).click()

    def navigate_to_subject_registration_form_tab(self):
        self.driver.find(SUBJECT_REG_FORM_TAB_LINK).click()

    def select_subject_by_uid(self, uid):
        self.driver.find(by_css(SUBJECT_CB_LOCATOR % str(uid))).click()

    def select_subject_by_row(self, row_number):
        self.driver.find(by_xpath(".//*[@id='subjects_table']/tbody/tr[%d]/td[1]/input" % row_number)).click()

    def wait_for_subject_table_to_load(self):
        WebDriverWait(self.driver, 1).until(
            lambda driver: driver.find(by_xpath(".//*[@id='subjects_table']/tbody/tr[2]/td[1]/input")).is_displayed())

    def click_checkall_checkbox(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, CHECKALL_CB, True)
        self.driver.find(CHECKALL_CB).click()

    def get_number_of_selected_subjects(self):
        return len([input_element for input_element in self.get_inputs_webelement() if
                    input_element.get_attribute("checked") == "true"])

    def get_inputs_webelement(self):
        return self.driver.find(by_id("subjects_table_wrapper")).find_elements(by="css selector",
                                                                               value="tbody tr td input")

    def get_all_subjects_count(self):
        return len(self.get_inputs_webelement())

    def is_checkall_checked(self):
        return self.driver.find(CHECKALL_CB).get_attribute("checked") == "true"

    def choose_question_type(self, type):
        if self.is_question_type_enabled():
            self.driver.find(by_css(SPECIFIC_TYPE_CB_BY_CSS % type)).click()

    def get_instruction_for_current_question(self):
        return self.driver.find(by_id("question_instruction")).text

    def click_register_subject(self):
        self.driver.find(REGISTER_SUBJECT_LINK).click()
        return AddSubjectPage(self.driver)

    def is_checkall_enabled(self):
        WebDriverWait(self.driver, UI_TEST_TIMEOUT).until(lambda driver: not driver.find(CHECKALL_CB).is_enabled())
        return self.driver.find(CHECKALL_CB).is_enabled()

    def is_checkall_disabled(self):
        WebDriverWait(self.driver, UI_TEST_TIMEOUT).until_not(lambda driver: driver.find(CHECKALL_CB).is_enabled(),
                                                message="Check-All box is not disabled")
        return not self.driver.find(CHECKALL_CB).is_enabled()