# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from framework.utils.common_utils import CommonUtilities
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from pages.allsubjectspage.all_subjects_locator import *
from pages.page import Page
from testdata.test_data import url
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage


class AllSubjectsPage(Page):
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
        if commUtils.is_element_present(by_xpath(SUBJECT_ACCORDION_LINK % subject)):
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
        