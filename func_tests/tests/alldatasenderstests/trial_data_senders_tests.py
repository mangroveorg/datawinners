import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver, HeadlessRunnerTest
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from framework.utils.database_manager_postgres import DatabaseManager
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from tests.endtoendtest.end_to_end_data import VALID_DATA_FOR_DATA_SENDER1, VALID_DATA_FOR_PROJECT, \
    QUESTIONS, CODE, QUESTION, QUESTIONNAIRE_CODE, DEFAULT_QUESTION, GEN_RANDOM, \
    TYPE, NUMBER, MIN, MAX, DATE, DATE_FORMAT, DD_MM_YYYY, CHARACTER_REMAINING, PAGE_TITLE
from tests.registrationtests.trial_registration_tests import register_and_get_email_for_trial
from tests.endtoendtest.end_to_end_tests import activate_account
from testdata.test_data import LOGOUT

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS01", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "WID"},
                      QUESTIONS: [{QUESTION: "Water Level", CODE: "WL", TYPE: NUMBER, MIN: "1", MAX: "1000"},
                                  {QUESTION: "Date of report in DD.MM.YYY format", CODE: "DMY", TYPE: DATE,
                                   DATE_FORMAT: DD_MM_YYYY}],
                      CHARACTER_REMAINING: "127 / 160 characters used",
                      PAGE_TITLE: "Data Senders"}

@attr("functional_test")
class TestTrialDataSenders(HeadlessRunnerTest):
    emails = []


    def create_questionnaire(self, create_questionnaire_page):
        create_questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA)
        create_data_sender_questionnaire_page = create_questionnaire_page.save_questionnaire_successfully()
        create_data_sender_questionnaire_page.save_questionnnaire_successfully().save_reminder_successfully()
        return create_data_sender_questionnaire_page

    def add_subject_type(self, valid_subject_type):
        add_subject_type_page = AddSubjectTypePage(self.driver)
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(valid_subject_type)


    def add_trial_organization_with_data_sender(self):
        registration_confirmation_page, email = register_and_get_email_for_trial(self.driver)
        self.emails.append(email)
        activate_account(self.driver, email)
        global_navigation_page = GlobalNavigationPage(self.driver)
        create_project_page = global_navigation_page.navigate_to_dashboard_page().navigate_to_create_project_page()
        questionnaire_page = create_project_page.select_blank_questionnaire_creation_option()
        questionnaire_page.create_questionnaire_with(VALID_DATA_FOR_PROJECT, QUESTIONNAIRE_DATA)
        questionnaire_page.save_and_create_project_successfully()

        add_data_sender_page = global_navigation_page.navigate_to_all_data_sender_page().navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_FOR_DATA_SENDER1)
        return add_data_sender_page

    def test_should_not_allow_data_senders_register_with_same_phone_number_for_different_accounts(self):
        add_data_sender_page = self.add_trial_organization_with_data_sender()
        self.assertIn("Your contact(s) have been added.", add_data_sender_page.get_success_message())
        self.driver.go_to(LOGOUT)
        add_data_sender_page = self.add_trial_organization_with_data_sender()
        self.assertEqual(
            "Sorry, this number has already been used for a different DataWinners Basic account.",
            add_data_sender_page.get_error_message())


    def tearDown(self):
        teardown_driver(self.driver)
        try:
            for email in self.emails:
                dbmanager = DatabaseManager()
                dbname = dbmanager.delete_organization_all_details(email)
                couchwrapper = CouchHttpWrapper()
                couchwrapper.deleteDb(dbname)
            pass
        except TypeError as e:
            pass