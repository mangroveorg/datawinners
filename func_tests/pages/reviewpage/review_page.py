# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.reviewpage.review_locator import *
from pages.smstesterlightbox.sms_tester_light_box_page import SMSTesterLightBoxPage
from tests.reviewandtests.review_data import *
import time
from pages.page import Page


class ReviewPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_project_overview_page(self):
        """
        Function to navigate to project overview page of the website

        Return project_overview_page
         """
        self.driver.find(GO_TO_PROJECT_OVERVIEW_BTN).click()
        from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage

        return ProjectOverviewPage(self.driver)

    def get_project_name(self):
        """
        Function to fetch the project name

        Return name
        """
        return self.driver.find(PROJECT_NAME_LABEL).text


    def get_project_description(self):
        """
        Function to fetch the project description

        Return message
        """
        return self.driver.find(PROJECT_DESCRIPTION_LABEL).text

    def get_devices(self):
        """
        Function to fetch the devices for project

        Return devices
        """
        return self.driver.find(DEVICES_LABEL).text

    def get_subject_type(self):
        """
        Function to fetch the subject type

        Return type
        """
        return self.driver.find(SUBJECT_TYPE_LABEL).text

    def get_subject_count(self):
        """
        Function to fetch the subject count

        Return count
        """
        return self.driver.find(SUBJECT_COUNT_LABEL).text

    def get_data_sender_count(self):
        """
        Function to fetch the data senders count

        Return count
        """
        return self.driver.find(DATA_SENDERS_COUNT_LABEL).text

    def get_questionnaire(self):
        """
        Function to fetch the subject count

        Return questionnaire list
        """
        questions_labels = self.driver.find_elements_(QUESTIONS_LABELS)
        questions = []
        for questions_label in questions_labels:
            questions.append(unicode(string=(questions_label.text)))
        return questions


    def get_subject_details(self):
        """
        Function to fetch the subjects details e.g. Type, count etc

        Return subject dict
        """
        subject_details = dict()
        subject_details[SUBJECT] = self.get_subject_type()
        #subject_details[SUBJECT_COUNT] = self.get_subject_count()
        return subject_details

    def open_accordion(self, accordion):
        """
        Function to open the subjects accordion
        """
        self.driver.find(by_css("div#%s .header" % accordion)).click()
        self.driver.wait_for_element(7, by_css("div#%s.ui-accordion .ui-accordion-content" % accordion), want_visible=True)

    def open_subject_accordion(self):
        self.open_accordion("subjects")

    def open_data_sender_accordion(self):
        self.open_accordion("data_senders")

    def open_questionnaire_accordion(self):
        self.open_accordion("questionnaire")

    def open_reminder_accordion(self):
        self.open_accordion("reminders")

    def open_sms_tester_light_box(self):
        """
        Function to open the sms tester light box

        return SMSTesterLightBoxPage
        """
        self.driver.find(SMS_QUESTIONNAIRE_LINK).click()
        return SMSTesterLightBoxPage(self.driver)
