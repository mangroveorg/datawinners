# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import time
from pages.lightbox.light_box_locator import TITLE_LABEL
from pages.lightbox.light_box_page import LightBox
from framework.utils.data_fetcher import *
from pages.createprojectpage.create_project_locator import *
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.page import Page
from framework.utils.common_utils import generateId, CommonUtilities

OTHER_SUBJECT = "other subject"
PROJECT_NAME = "project_name"
PROJECT_BACKGROUND = "project_background"
PROJECT_TYPE = "project_type"
REPORT_TYPE = "report_type"
SUBJECT = "subject"
DEVICES = "devices"
GEN_RANDOM = "gen_random"
SURVEY = "survey"
PUBLIC_INFO = "public information"
DATA_SENDER_WORK = "data sender work"


class CreateProjectPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def select_report_type(self, project_data):
        report_type = fetch_(REPORT_TYPE, from_(project_data))
        if report_type == DATA_SENDER_WORK:
            self.driver.find(DATA_SENDER_RB).click()
        elif report_type == OTHER_SUBJECT:
            self.driver.find(OTHER_SUBJECT_RB).click()
        return LightBox(self.driver)

    def select_project_type(self, project_data):
        project_type = fetch_(PROJECT_TYPE, from_(project_data))
        if project_type == SURVEY:
            self.driver.find(SURVEY_PROJECT_RB).click()
        elif project_type == PUBLIC_INFO:
            self.driver.find(PUBLIC_INFORMATION_RB).click()

    def type_project_description(self, project_data):
        self.driver.find_text_box(PROJECT_BACKGROUND_TB).enter_text(
            fetch_(PROJECT_BACKGROUND, from_(project_data)))

    def type_project_name(self, project_data):
        project_name = fetch_(PROJECT_NAME, from_(project_data))
        try:
            gen_random = fetch_(GEN_RANDOM, from_(project_data))
        except KeyError:
            gen_random = False
        if gen_random:
            project_name += generateId()
        self.driver.find_text_box(PROJECT_NAME_TB).enter_text(project_name)

    def create_project_with(self, project_data):
        """
        Function to enter and save the data on set up project page

        Args:
        project_data is data to fill in the different fields

        Return self
        """
        self.type_project_name(project_data)
        self.type_project_description(project_data)
        light_box = self.select_report_type(project_data)
        comm_util = CommonUtilities(self.driver)
        if comm_util.is_element_present(TITLE_LABEL):
            light_box.continue_change()
        self.set_subject(project_data)
        if comm_util.is_element_present(TITLE_LABEL):
            light_box.continue_change()
        return self

    def save_and_create_project_successfully(self, click_ok=True):
        self.driver.find(SAVE_AND_CREATE_BTN).click()
        time.sleep(3)
        if click_ok:
            self.got_redistribute_questionnaire_message()
        return ProjectOverviewPage(self.driver)

    def save_and_create_project(self, click_ok=True):
        self.driver.find(SAVE_AND_CREATE_BTN).click()
        if click_ok:
            self.got_redistribute_questionnaire_message()
        return self

    def continue_create_project(self):
        return self.driver.find(CONTINUE_BTN).click()

    def set_subject(self, project_data):
        subject = fetch_(SUBJECT, from_(project_data))
        if len(subject):
            self.driver.find_drop_down(SUBJECTS_DD).set_selected(subject)
        return self

    def edit_subject(self, project_data):
        subject = fetch_(SUBJECT, from_(project_data))
        self.driver.find_drop_down(SUBJECTS_DD).set_selected(subject)
        return LightBox(self.driver)

    def get_error_message(self):
        """
        Function to fetch the error messages from error label of the register
        reporter page

        Return error message
        """
        error_message = ""
        comm_utils = CommonUtilities(self.driver)
        locator = comm_utils.is_element_present(PROJECT_NAME_ERROR_MSG_LABEL)
        if locator:
            error_message = error_message + "Name  " + locator.text
            #        locator = comm_utils.is_element_present(PROJECT_TYPE_ERROR_MSG_LABEL)
        #        if locator:
        #            error_message = error_message + "Project Type  " + locator.text
        #        locator = comm_utils.is_element_present(QUESTIONNAIRE_ABOUT_MSG_LABEL)
        #        if locator:
        #            error_message = error_message + "Activity Report Type  " + locator.text
        return error_message == "" and "No error message on the page" or error_message

    def get_selected_subject(self):
        """
        Function to fetch the selected subject from the drop down

        Return message
        """
        return self.driver.find_drop_down(SUBJECTS_DD).get_selected()

    def get_project_name(self):
        """
        Function to fetch the project name

        Return message
        """
        return self.driver.find_text_box(PROJECT_NAME_TB).get_attribute("value")

    def get_project_type(self):
        """
        Function to fetch the project type e.g. Survey or Public info

        Return message
        """
        project_type = ""
        if self.driver.find_radio_button(SURVEY_PROJECT_RB).is_selected():
            project_type = SURVEY
        elif self.driver.find_radio_button(PUBLIC_INFORMATION_RB).is_selected():
            project_type = PUBLIC_INFO
        return project_type

    def get_project_description(self):
        """
        Function to fetch the project description

        Return message
        """
        return self.driver.find_text_box(PROJECT_BACKGROUND_TB).text

    def get_devices(self):
        """
        Function to fetch the devices for project

        Return message
        """
        return "sms"

    def get_report_type(self):
        """
        Function to fetch the report type e.g. other subject or Activity report

        Return message
        """
        report_type = ""
        if self.driver.find_radio_button(OTHER_SUBJECT_RB).is_selected():
            report_type = OTHER_SUBJECT
        elif self.driver.find_radio_button(DATA_SENDER_RB).is_selected():
            report_type = DATA_SENDER_WORK
        return report_type

    def get_project_details(self):
        """
        Function to fetch the project details e.g. Name, Type, description etc

        Return message
        """
        project_details = dict()
        project_details[PROJECT_NAME] = self.get_project_name()
        project_details[PROJECT_BACKGROUND] = self.get_project_description()
        #project_details[PROJECT_TYPE] = self.get_project_type()
        project_details[REPORT_TYPE] = self.get_report_type()
        if project_details[REPORT_TYPE] == OTHER_SUBJECT:
            project_details[SUBJECT] = self.get_selected_subject()
        else:
            project_details[SUBJECT] = ""
            #project_details[DEVICES] = self.get_devices()
        return project_details

    def select_predefined_periodicity_question_text(self):
        self.driver.find_text_box(by_id("question_title")).click()

    def get_warning_message(self):
        return self.driver.find(by_css("#periode_green_message")).text

    def description_has_error(self):
        comm_util = CommonUtilities(self.driver)
        if comm_util.is_element_present(PROJECT_DESCRIPTION_MSG):
            return True
        return False

    def got_redistribute_questionnaire_message(self):
        comm_utils = CommonUtilities(self.driver)
        locator = comm_utils.is_element_present(INFORM_DATASENDERS_OK_BUTTON_BY_CSS)
        if locator and locator.is_displayed():
            locator.click()