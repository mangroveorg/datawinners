# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.lightbox.light_box_locator import *
from pages.page import Page


class LightBox(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def activate_project(self):
        """
        Function to activate the project

        Return ProjectOverviewPage
         """
        self.driver.find(ACTIVATE_BTN).click()
        from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage

        return ProjectOverviewPage(self.driver)

    def continue_change(self):
        """
        Function to continue the subject change

        Return CreateProjectPage
         """
        self.driver.find(CONFIRMATION_BTN).click()
        from pages.createprojectpage.create_project_page import CreateProjectPage

        return CreateProjectPage(self.driver)

    def cancel_light_box(self):
        """
        Function to cancel the activation of a project

        Return create project page
         """
        self.driver.find(CANCEL_LINK).click()
        return self

    def close_light_box(self):
        """
        Function to close the activation light box of a project

        Return create project page
         """
        self.driver.find(CLOSE_BTN).click()
        return self

    def get_message_from_light_box(self):
        """
        Function to fetch the message from light box

        Return message text
         """
        return self.driver.find(MESSAGE_LABEL).text

    def get_title_of_light_box(self):
        """
        Function to fetch the title from light box

        Return title text
         """
        return self.driver.find(TITLE_LABEL).text

    def continue_change_date_format(self):
        """
        Function to continue the subject change

        Return CreateProjectPage
         """
        self.driver.find(CHANGE_DATE_FORMAT_CONTINUE_BTN).click()
        from pages.createprojectpage.create_project_page import CreateProjectPage

        return CreateProjectPage(self.driver)