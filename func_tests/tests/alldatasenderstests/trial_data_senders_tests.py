from framework.base_test import BaseTest
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from framework.utils.database_manager_postgres import DatabaseManager
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from tests.endtoendtest.end_to_end_data import VALID_DATA_FOR_DATA_SENDER1, VALID_DATA_FOR_PROJECT, \
    VALID_SUBJECT_TYPE2, QUESTIONS, CODE, QUESTION, QUESTIONNAIRE_CODE, DEFAULT_QUESTION, GEN_RANDOM, \
    TYPE, NUMBER, MIN, MAX, ENTITY_TYPE, DATE, DATE_FORMAT, DD_MM_YYYY, CHARACTER_REMAINING, PAGE_TITLE, \
    INVALID_DATA_FOR_DATA_SENDER
from tests.registrationtests.registration_data import REGISTRATION_PASSWORD
from tests.registrationtests.trial_registration_tests import register_and_get_email_for_trial
from tests.endtoendtest.end_to_end_tests import activate_account, do_login
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from nose.plugins.attrib import attr

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS01", GEN_RANDOM: False,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "WID"},
                      QUESTIONS: [{QUESTION: "Water Level", CODE: "WL", TYPE: NUMBER, MIN: "1", MAX: "1000"},
                              {QUESTION: "Date of report in DD.MM.YYY format", CODE: "DMY", TYPE: DATE,
                               DATE_FORMAT: DD_MM_YYYY}],
                      CHARACTER_REMAINING: "127 / 160 characters used",
                      PAGE_TITLE: "Data Senders"}


class TestTrialDataSenders(BaseTest):
    emails = []

    def add_trial_organization_and_login(driver):
        registration_confirmation_page, email = register_and_get_email_for_trial(driver)
        activate_account(driver, email)
        return do_login(driver, email, REGISTRATION_PASSWORD)

    def create_questionnaire(self, create_questionnaire_page):
        create_questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA)
        create_data_sender_questionnaire_page = create_questionnaire_page.save_questionnaire_successfully()
        create_data_sender_questionnaire_page.save_questionnnaire_successfully().save_reminder_successfully()
        return create_data_sender_questionnaire_page

    def add_subject_type(self, valid_subject_type):
        add_subject_type_page = AddSubjectTypePage(self.driver)
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(valid_subject_type)

    def create_project(self, create_project_page):
        create_project_page.select_report_type(VALID_DATA_FOR_PROJECT)
        self.add_subject_type(VALID_SUBJECT_TYPE2[ENTITY_TYPE])
        return create_project_page.create_project_with(VALID_DATA_FOR_PROJECT).continue_create_project().save_and_create_project_successfully()

    def add_trial_organization_with_data_sender(self):
        registration_confirmation_page, email = register_and_get_email_for_trial(self.driver)
        self.emails.append(email)
        activate_account(self.driver, email)
        global_navigation = do_login(self.driver, email, REGISTRATION_PASSWORD)
        # create a project
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        self.create_project(dashboard_page.navigate_to_create_project_page()) #TODO There was some code related to creating a questionnaire. We have removed it in a deliberate attempt to fix the test. Kindly review the code. Diptanu/Neetu

        add_data_sender_page = global_navigation.navigate_to_all_data_sender_page().navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_FOR_DATA_SENDER1)
        return add_data_sender_page

    def test_should_not_allow_data_senders_register_with_same_phone_number_for_different_accounts(self):
        add_data_sender_page = self.add_trial_organization_with_data_sender()
        self.assertIn("Registration successful.", add_data_sender_page.get_success_message())
        self.driver.go_to('http://localhost:8000/logout/')
        add_data_sender_page = self.add_trial_organization_with_data_sender()
        self.assertEqual("Mobile Number Sorry, this number has already been used for a different DataWinners trial account.", add_data_sender_page.get_error_message())


    def tearDown(self):
        try:
            self.driver.quit()
            for email in self.emails:
                dbmanager = DatabaseManager()
                dbname = dbmanager.delete_organization_all_details(email)
                couchwrapper = CouchHttpWrapper("localhost")
                couchwrapper.deleteDb(dbname)
            pass
        except TypeError as e:
            pass

    @attr('functional_test')
    def test_should_get_user_focus_on_first_error_field(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        global_navigation = login_page.do_successful_login_with(VALID_CREDENTIALS)
        add_data_sender_page = global_navigation.navigate_to_all_data_sender_page().navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(INVALID_DATA_FOR_DATA_SENDER)
        self.assertEqual(add_data_sender_page.get_error_message(), u'Mobile Number This field is required.')
        a = self.driver.switch_to_active_element()
        self.assertEqual(a.get_attribute("id"), u"id_telephone_number")