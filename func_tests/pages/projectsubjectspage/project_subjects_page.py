from pages.page import Page
from pages.projectsubjectspage.project_subjects_locator import EDIT_FORM_LINK, EDIT_CONTINUE_LINK, ADD_QUESTION_LINK, \
    SELECTED_QUESTION_LABEL, SUBMIT_BTN, SUCCESS_MESSAGE_TIP, TYPE_CB, ACTION_DROP_DOWN, EDIT_LI_LOCATOR, \
    NONE_SELECTED_LOCATOR, ACTION_MENU, MY_SUBJECTS_TAB_LINK, SUBJECT_CB_LOCATOR, SUCCESS_MESSAGE_TIP
from framework.utils.common_utils import by_css

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

    def is_edit_enabled(self):
        css_class = self.driver.find(EDIT_LI_LOCATOR).get_attribute("class")
        return css_class.find("disabled") < 0

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def navigate_to_my_subjects_list_tab(self):
        self.driver.find(MY_SUBJECTS_TAB_LINK).click()

    def select_subject_by_uid(self, uid):
        self.driver.find(by_css(SUBJECT_CB_LOCATOR % str(uid))).click()
