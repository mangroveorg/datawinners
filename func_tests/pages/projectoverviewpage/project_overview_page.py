# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.broadcastSMSpage.broadcast_sms_page import BroadcastSmsPage
from pages.dataanalysispage.data_analysis_page import DataAnalysisPage
from pages.lightbox.light_box_page import LightBox
from pages.projectdatasenderspage.project_data_senders_page import ProjectDataSendersPage
from pages.projectoverviewpage.project_overview_locator import *
from pages.page import Page
from pages.projectsubjectspage.project_subjects_page import ProjectSubjectsPage
from pages.reminderpage.all_reminder_page import AllReminderPage
from pages.smstesterlightbox.sms_tester_light_box_page import SMSTesterLightBoxPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage


class ProjectOverviewPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_data_page(self):
        self.driver.find(DATA_TAB).click()
        return DataAnalysisPage(self.driver)

    def navigate_to_datasenders_page(self):
        self.driver.find(DATASENDERS_TAB).click()
        return ProjectDataSendersPage(self.driver)

    def navigate_to_subjects_page(self):
        self.driver.find(SUBJECTS_TAB).click()
        return ProjectSubjectsPage(self.driver)

    def subject_tab_text(self):
        return self.driver.find(SUBJECTS_TAB).text

    def navigate_to_reminder_page(self):
        self.driver.find(MESSAGES_AND_REMINDERS_TAB).click()
        return AllReminderPage(self.driver)

    def navigate_to_edit_project_page(self):
        self.driver.find(PROJECT_EDIT_LINK).click()
        from pages.questionnairetabpage.questionnaire_tab_page import QuestionnaireTabPage
        return QuestionnaireTabPage(self.driver)

    def get_status_of_the_project(self):
        return self.driver.find(PROJECT_STATUS_LABEL).text

    def open_sms_tester_light_box(self):
        self.driver.find(TEST_QUESTIONNAIRE_LINK).click()
        return SMSTesterLightBoxPage(self.driver)

    def navigate_send_message_tab(self):
        self.driver.find(SEND_MESSAGE_TAB).click()
        return BroadcastSmsPage(self.driver)

    def open_sms_questionnaire_preview(self):
        self.driver.find(by_css(".sms_questionnaire")).click()
        return LightBox(self.driver)

    def navigate_to_questionnaire_tab(self):
        self.driver.find(QUESTIONNAIRE_TAB).click()
        from pages.questionnairetabpage.questionnaire_tab_page import QuestionnaireTabPage
        return QuestionnaireTabPage(self.driver)

    def get_project_title(self):
        self.driver.wait_for_element(60, PROJECT_TITLE_LOCATOR, True)
        return self.driver.find(PROJECT_TITLE_LOCATOR).text.lower()

    def get_questionnaire_code(self):
        url_data_tab = self.driver.find(DATA_TAB).get_attribute("href")
        return url_data_tab.split("/")[6]

    def navigate_to_web_questionnaire_page(self):
        self.driver.find(WEB_QUESTIONNAIRE_PAGE).click()
        return WebSubmissionPage(self.driver)