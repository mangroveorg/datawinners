# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from time import sleep
from pages.alldatapage.all_data_page import AllDataPage
from pages.allsubjectspage.all_subject_type_page import AllSubjectTypePage
from pages.dashboardpage.dashboard_page import DashboardPage
from pages.globalnavigationpage.global_navigation_locator import *
from pages.languagespage.customized_languages_page import CustomizedLanguagePage
from pages.page import Page
from pages.projectspage.projects_page import ProjectsPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from pages.reportspage.reports_page import ReportsPage
from tests.testsettings import UI_TEST_TIMEOUT


class GlobalNavigationPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def welcome_message(self):
        """
        Function to fetch the Welcome message from the label provided on
        dashboard page.

        Return the Welcome message
         """
        welcome_message = self.driver.find(WELCOME_MESSAGE_LABEL).text
        return welcome_message

    def navigate_to_all_data_sender_page(self):
        """
        Function to navigate to all data sender page of the website.

        Return add data sender page
         """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DATA_SENDERS_LINK, True)
        self.driver.find(DATA_SENDERS_LINK).click()
        return AllDataSendersPage(self.driver)

    def navigate_to_view_all_project_page(self):
        """
        Function to navigate to view all projects page of the website.

        Return view all projects page
         """
        self.driver.find(PROJECT_LINK).click()
        return ProjectsPage(self.driver)

    def click_on_save_change(self):
        """
        Function to navigate to view all projects page of the website.

        Return view all projects page
         """
        self.driver.find("#save_changes").click()
        return ProjectsPage(self.driver)

    def navigate_to_all_subject_page(self):
        """
        Function to navigate to add a subject page of the website.

        Return add subject page
         """
        self.driver.find(SUBJECTS_LINK).click()
        return AllSubjectTypePage(self.driver)

    def navigate_to_dashboard_page(self):
        """
        Function to navigate to dashboard page of the website

        Return dashboard page
         """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, DASHBOARD_PAGE_LINK, True)
        self.driver.find(DASHBOARD_PAGE_LINK).click()
        try:
            self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Dashboard")
        except Exception as e:
            self.driver.create_screenshot("debug-ft-navigate-to-dashboard-fails")
            raise e
        return DashboardPage(self.driver)

    def navigate_to_all_data_page(self):
        """
        Function to navigate to all data page of the website.

        Return add data sender page
         """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, PROJECT_LINK, True)
        self.driver.find(PROJECT_LINK).click()
        return AllDataPage(self.driver)

    def sign_out(self):
        """
        Function to sign out from any account
        """
        self.driver.wait_for_element(UI_TEST_TIMEOUT, SIGN_OUT_LINK, True)
        self.driver.find(SIGN_OUT_LINK).click()
        self.driver.wait_for_page_load()

    def navigate_to_languages_page(self):
        self.driver.find(LANGUAGES_LINK).click()
        return CustomizedLanguagePage(self.driver)

    def navigate_to_reports_page(self):
        self.driver.find(REPORTS_LINK).click()
        self.driver.wait_for_page_load()
        return ReportsPage(self.driver)

