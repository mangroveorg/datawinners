# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.global_constant import WAIT_FOR_TITLE
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.createsubjectquestionnairepage.create_subject_questionnaire_locator import *
from pages.page import Page


class CreateSubjectQuestionnairePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def save_questionnaire_successfully(self):
        """
        Function to save subject questionnaire

        Args:
        subject_data is data to fill in the different fields

        Return CreateQuestionnairePage
        """
        self.driver.find(SAVE_CHANGES_BTN).click()
        self.driver.wait_for_page_with_title( WAIT_FOR_TITLE, "Questionnaire")
        return CreateQuestionnairePage(self.driver)

    def navigate_to_previous_step(self):
        """
        Function to go on set up project profile page

        Return self
        """
        self.driver.find(PREVIOUS_STEP_LINK).click()
        from pages.createprojectpage.create_project_page import CreateProjectPage

        return CreateProjectPage(self.driver)

    def get_page_title(self):
        """
        Function to return the page title

        Return title
        """
        return "Subjects"
