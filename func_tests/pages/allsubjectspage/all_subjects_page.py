# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from pages.allsubjectspage.all_subjects_locator import *
from pages.page import Page


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
