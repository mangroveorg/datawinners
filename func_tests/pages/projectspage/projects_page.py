# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from string import lower
from pages.createprojectpage.questionnaire_creation_options_page import QuestionnaireCreationOptionsPage
from pages.lightbox.light_box_page import LightBox
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.projectspage.projects_locator import *
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT


class ProjectsPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_create_project_page(self):
        """
        Function to navigate to create project page of the website.

        Return create project page
         """
        self.driver.find(CREATE_A_NEW_PROJECT_LINK).click()
        return QuestionnaireCreationOptionsPage(self.driver)

    def wait_for_page_to_load(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_id('create_project_link'), True)

    def navigate_to_project_overview_page(self, project_name):
        """
        Function to navigate to specific project overview page

        Return project overview page
         """
        project_link = by_xpath(PROJECT_LINK_XPATH % project_name)
        self.driver.wait_for_element(UI_TEST_TIMEOUT, project_link, True)
        self.driver.find(project_link).click()
        return ProjectOverviewPage(self.driver)

    def is_project_present(self, project_name):
        all_project_elements = self.driver.find_elements_(by_css(".styled_table tbody tr td a"))
        all_project_names = [element.text for element in all_project_elements]
        return project_name in all_project_names

    def delete_project(self, project_name):
        project_rows = self.driver.find_elements_(by_css(".styled_table tbody tr"))
        for row in project_rows:
            if project_name == row.find_element_by_class_name('project-id-class ').text:
                row.find_element_by_class_name('delete_project').click()
                self.driver.find(by_css('a#confirm_delete')).click()
                return
        raise CouldNotLocateElementException(['.styled_table tbody tr', 'project-id-class', 'delete_project'], 'by_css')


    def trigger_undo_delete(self):
        self.driver.find_visible_element(by_id("undo_delete_project")).click()
        return self

    def click_on_save_changes(self):
        self.driver.find(by_css('#save_changes')).click()
