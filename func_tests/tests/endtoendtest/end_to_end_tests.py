# vim: ai ts=4 sts=4 et sw=4utf-8
from unittest import SkipTest
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.common_utils import get_epoch_last_ten_digit
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.database_manager_postgres import DatabaseManager
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.loginpage.login_page import LoginPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_DASHBOARD_PAGE
from tests.endtoendtest.end_to_end_data import *
from tests.registrationtests.registration_tests import register_and_get_email


def activate_account(driver, email):
    account_activate_page = ActivateAccountPage(driver)
    dbmanager = DatabaseManager()
    activation_code = dbmanager.get_activation_code(email)
    account_activate_page.activate_account(activation_code)
    return account_activate_page


def do_login(driver, email, password):
    driver.go_to(DATA_WINNER_LOGIN_PAGE)
    login_page = LoginPage(driver)
    return login_page.do_successful_login_with({USERNAME: email, PASSWORD: password})


@attr('suit_2')
class TestApplicationEndToEnd(BaseTest):
    def tearDown(self):
        import sys

        exception_info = sys.exc_info()
        if exception_info != (None, None, None):
            import os

            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            self.driver.get_screenshot_as_file(
                "screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))

        try:
            self.driver.quit()
            if self.email is not None:
                email = self.email
                dbmanager = DatabaseManager()
                dbname = dbmanager.delete_organization_all_details(email.lower())
                couchwrapper = CouchHttpWrapper()
                couchwrapper.deleteDb(dbname)
        except TypeError as e:
            pass

    def activate_account(self):
        account_activate_page = activate_account(self.driver, self.email.lower())
        self.assertRegexpMatches(account_activate_page.get_message(),
                                 fetch_(SUCCESS_MESSAGE, from_(VALID_ACTIVATION_DETAILS)))

    def set_organization_number(self):
        dbmanager = DatabaseManager()
        organization_sms_tel_number = get_epoch_last_ten_digit()
        dbmanager.set_sms_telephone_number(organization_sms_tel_number, self.email.lower())
        return organization_sms_tel_number

    def do_org_registartion(self):
        registration_confirmation_page, self.email = register_and_get_email(self.driver)
        self.assertEquals(registration_confirmation_page.registration_success_message(),
                          fetch_(SUCCESS_MESSAGE, from_(REGISTRATION_DATA_FOR_SUCCESSFUL_REGISTRATION)))

    def do_login(self):
        global_navigation = do_login(self.driver, self.email, REGISTRATION_PASSWORD)
        self.assertEqual(global_navigation.welcome_message(), "Welcome Mickey!")
        return global_navigation

    def add_a_data_sender(self, dashboard_page):
        add_data_sender_page = dashboard_page.navigate_to_add_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_FOR_DATA_SENDER)
        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_FOR_DATA_SENDER)))

    def add_subject_type(self, create_project_page, entity_type):
        add_subject_type_page = AddSubjectTypePage(self.driver)
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(entity_type)
        self.assertEqual(create_project_page.get_selected_subject(), entity_type.lower())

    def add_a_subject(self, add_subject_page):
        add_subject_page.add_subject_with(VALID_DATA_FOR_SUBJECT)
        add_subject_page.submit_subject()
        self.assertEqual(add_subject_page.get_flash_message(), fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_FOR_SUBJECT)))

    def add_a_data_sender(self, add_data_sender_page):
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_FOR_DATA_SENDER)
        self.assertEqual(add_data_sender_page.get_success_message(),
                         fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_FOR_DATA_SENDER)))

    def create_project(self, create_project_page):
        create_project_page.create_project_with(VALID_DATA_FOR_PROJECT)
        create_project_page.continue_create_project()
        return CreateQuestionnairePage(self.driver)

    def create_questionnaire(self, create_questionnaire_page):
        create_questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA)
        index = 3
        for question in fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA)):
            question_link_text = fetch_(QUESTION, from_(question))
            self.assertEquals(create_questionnaire_page.get_question_link_text(index), question_link_text)
            index += 1
        self.assertEquals(create_questionnaire_page.get_remaining_character_count(),
                          fetch_(CHARACTER_REMAINING, from_(QUESTIONNAIRE_DATA)))
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully()
        return project_overview_page

    def send_sms(self, organization_sms_tel_number, sms):
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_data = sms
        sms_tester_data[RECEIVER] = str(organization_sms_tel_number)
        sms_tester_page.send_sms_with(sms_tester_data)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, from_(sms_tester_data)))
        return sms_tester_page

    def verify_submission1(self, global_navigation, sms_log):
        view_all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_project = view_all_project_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, VALID_DATA_FOR_PROJECT).lower())
        data_page = project_overview_project.navigate_to_data_page()
        submission_log_page = data_page.navigate_to_all_data_record_page()
        self.assertRegexpMatches(submission_log_page.get_submission_message(sms_log),
                                 fetch_(SMS_SUBMISSION, from_(sms_log)))

    def verify_submission2(self, global_navigation, sms_log):
        view_all_data_page = global_navigation.navigate_to_all_data_page()
        submission_log_page = view_all_data_page.navigate_to_submission_log_page_from_project_dashboard(
            fetch_(PROJECT_NAME, VALID_DATA_FOR_PROJECT).lower())
        self.assertRegexpMatches(submission_log_page.get_submission_message(sms_log),
                                 fetch_(SMS_SUBMISSION, from_(sms_log)))
        self.assertEqual(self.driver.get_title(), "Submission Log")

    def review_project_summary(self, review_page):
        self.assertEqual(fetch_(PROJECT_PROFILE, from_(VALID_DATA_REVIEW_AND_TEST)),
                         review_page.get_project_profile_details())
        review_page.open_subject_accordion()
        self.assertEqual(fetch_(SUBJECT_DETAILS, from_(VALID_DATA_REVIEW_AND_TEST)), review_page.get_subject_details())
        # unreliable in firefox in CI, works fine locally
        #        review_page.open_data_sender_accordion()
        #        self.assertEqual(fetch_(DATA_SENDER_COUNT, from_(VALID_DATA_REVIEW_AND_TEST)),
        #                         review_page.get_data_sender_count())
        review_page.open_questionnaire_accordion()
        self.assertEqual(fetch_(QUESTIONNAIRE, from_(VALID_DATA_REVIEW_AND_TEST)), review_page.get_questionnaire())

    def sms_light_box_verification(self, sms_tester_light_box):
        sms_tester_light_box.send_sms_with(VALID_DATA_FOR_SMS_LIGHT_BOX)
        self.assertEqual(sms_tester_light_box.get_response_message(),
                         fetch_(RESPONSE_MESSAGE, from_(VALID_DATA_FOR_SMS_LIGHT_BOX)))
        sms_tester_light_box.close_light_box()

    def verify_questionnaire(self, edit_questionnaire_page):
        questions = fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA))
        edit_questionnaire_page.select_question_link(3)
        self.assertEqual(questions[0], edit_questionnaire_page.get_number_type_question())
        edit_questionnaire_page.select_question_link(4)
        self.assertEqual(questions[1], edit_questionnaire_page.get_date_type_question())
        edit_questionnaire_page.select_question_link(5)
        self.assertEqual(questions[2], edit_questionnaire_page.get_date_type_question())
        edit_questionnaire_page.select_question_link(6)
        self.assertEqual(questions[3], edit_questionnaire_page.get_date_type_question())
        edit_questionnaire_page.select_question_link(7)
        self.assertEqual(questions[4], edit_questionnaire_page.get_list_of_choices_type_question())
        edit_questionnaire_page.select_question_link(8)
        self.assertEqual(questions[5], edit_questionnaire_page.get_word_type_question())
        edit_questionnaire_page.select_question_link(9)
        self.assertEqual(questions[6], edit_questionnaire_page.get_list_of_choices_type_question())
        edit_questionnaire_page.select_question_link(10)
        edit_questionnaire_page.select_question_link(10)
        self.assertEqual(questions[7], edit_questionnaire_page.get_geo_type_question())

    def edit_questionnaire(self, edit_questionnaire_page):
        questions = fetch_(QUESTIONS, from_(NEW_QUESTIONNAIRE_DATA))
        edit_questionnaire_page.select_question_link(3)
        edit_questionnaire_page.configure_number_type_question(questions[0])
        edit_questionnaire_page.add_question(questions[1])
        self.assertEquals(edit_questionnaire_page.get_remaining_character_count(),
                          fetch_(CHARACTER_REMAINING, from_(NEW_QUESTIONNAIRE_DATA)))
        edit_questionnaire_page.save_and_create_project_successfully()

    @SkipTest
    @attr('functional_test', 'smoke', "intregation")
    def test_end_to_end(self):
        """todo: failed randomly when run ft"""
        self.email = None
        self.do_org_registartion()

        organization_sms_tel_number = self.set_organization_number()
        self.activate_account()
        global_navigation = self.do_login()

        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.select_report_type(VALID_DATA_FOR_PROJECT)
        self.add_subject_type(create_project_page, VALID_SUBJECT_TYPE2[ENTITY_TYPE])
        self.add_subject_type(create_project_page, VALID_SUBJECT_TYPE1[ENTITY_TYPE])
        create_questionnaire_page = self.create_project(create_project_page)
        self.create_questionnaire(create_questionnaire_page)

        global_navigation.navigate_to_all_subject_page()
        add_subject_page = AddSubjectPage(self.driver)
        self.driver.go_to("http://localhost:8000/entity/subject/create/waterpoint/")
        self.add_a_subject(add_subject_page)

        all_data_senders_page = global_navigation.navigate_to_all_data_sender_page()
        add_data_sender_page = all_data_senders_page.navigate_to_add_a_data_sender_page()
        self.add_a_data_sender(add_data_sender_page)

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        self.send_sms(organization_sms_tel_number, VALID_DATA_FOR_SMS)

        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        self.verify_submission1(global_navigation, SMS_DATA_LOG)

        all_projects_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_page = all_projects_page.navigate_to_project_overview_page(
            fetch_(PROJECT_NAME, from_(VALID_DATA_FOR_PROJECT)))
        edit_project_page = project_overview_page.navigate_to_edit_project_page()
        edit_project_page.continue_create_project()
        edit_questionnaire_page = create_questionnaire_page
        self.verify_questionnaire(edit_questionnaire_page)
        self.edit_questionnaire(edit_questionnaire_page)

        all_projects_page = global_navigation.navigate_to_view_all_project_page()
        project_name = fetch_(PROJECT_NAME, from_(VALID_DATA_FOR_PROJECT))
        activate_project_light_box = all_projects_page.open_activate_project_light_box(project_name)
        self.assertEqual(activate_project_light_box.get_title_of_light_box(), "Activate this Project?")
        project_overview_page = activate_project_light_box.activate_project()
        self.assertEqual(project_overview_page.get_status_of_the_project(), "Active")

        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        self.send_sms(organization_sms_tel_number, NEW_VALID_DATA_FOR_SMS)

        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        self.verify_submission2(global_navigation, NEW_SMS_DATA_LOG)
