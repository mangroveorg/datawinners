# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.createprojectpage.questionnaire_creation_options_page import QuestionnaireCreationOptionsPage
from pages.dashboardpage.dashboard_locator import *
from pages.page import Page
from tests.testsettings import UI_TEST_TIMEOUT
from pages.broadcastSMSpage.broadcast_sms_page import BroadcastSmsPage


class DashboardPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_create_project_page(self):
        self.driver.find(CREATE_PROJECT_LINK).click()
        return QuestionnaireCreationOptionsPage(self.driver)

    def is_lightbox_open(self):
        return self.driver.find(LIGHTBOX_LOCATOR).is_displayed()

    def open_take_a_tour_video(self):
        self.driver.find(TAKE_A_TOUR_LOCATOR).click()

    def close_lightbox(self):
        self.driver.find(CLOSE_LIGHTBOX_LOCATOR).click()

    def open_get_started_video(self):
        self.driver.find(GET_STARTED_LOCATOR).click()

    
    def close_help_element(self):
        self.driver.find(CLOSE_HELP_ELEMENT_BUTTON).click()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, HELP_DIALOG, True)
        self.driver.find(CLOSE_HELP_DIALOG).click()
        self.driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, HELP_DIALOG)

    def is_help_element_present(self):
        return self.driver.is_element_present(HELP_ELEMENT_WELCOME)

    def get_projects_list(self):
        return [project.text for project in self.driver.find_elements_(PROJECTS_LIST_LOCATOR)]

    def click_on_send_a_message(self):
        self.driver.find(SEND_A_MSG_LINK_LOCATOR).click()
        return BroadcastSmsPage(self.driver)