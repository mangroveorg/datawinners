from pages.page import Page
from pages.projectsubjectspage.project_subjects_locator import EDIT_FORM_LINK, EDIT_CONTINUE_LINK, ADD_QUESTION_LINK, \
    SELECTED_QUESTION_LABEL, SUBMIT_BTN, SUCCESS_MESSAGE_TIP, TYPE_CB

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