# vim: ai ts=4 sts=4 et sw=4utf-8
import unittest
import time

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36
from nose.plugins.attrib import attr

from framework.base_test import teardown_driver, setup_driver
from framework.utils.common_utils import get_epoch_last_ten_digit, generate_random_email_id, by_css
from framework.utils.couch_http_wrapper import CouchHttpWrapper
from framework.utils.data_fetcher import from_, fetch_
from framework.utils.database_manager_postgres import DatabaseManager
from pages.activateaccountpage.activate_account_page import ActivateAccountPage
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from pages.allsubjectspage.add_subject_page import AddSubjectPage
from pages.addsubjecttypepage.add_subject_type_page import AddSubjectTypePage
from pages.allsubjectspage.all_subject_type_page import AllSubjectTypePage
from pages.allsubjectspage.all_subjects_list_page import AllSubjectsListPage
from pages.createquestionnairepage.create_questionnaire_page import CreateQuestionnairePage
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.submissionlogpage.submission_log_locator import EDIT_BUTTON, DELETE_BUTTON
from pages.submissionlogpage.submission_log_page import SubmissionLogPage
from pages.warningdialog.warning_dialog import WarningDialog
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from testdata.constants import SUCCESS_MSG
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_DASHBOARD_PAGE, LOGOUT, url
from tests.activateaccounttests.activate_account_data import DS_ACTIVATION_URL, NEW_PASSWORD
from tests.alldatasenderstests.add_data_senders_data import VALID_DATA_WITH_EMAIL, VALID_DATA_WITH_EMAIL_FOR_EDIT
from tests.endtoendtest.end_to_end_data import *
from tests.projects.questionnairetests.project_questionnaire_data import VALID_SUMMARY_REPORT_DATA
from tests.registrationtests.registration_tests import register_and_get_email
from pages.alldatasenderspage.all_data_senders_locator import DELETE_BUTTON as CONFIRM_DELETE
from tests.registrationtests.trial_registration_tests import register_and_get_email_for_trial
from tests.testsettings import UI_TEST_TIMEOUT

def add_trial_organization_and_login(driver):
    registration_confirmation_page, email = register_and_get_email_for_trial(driver)
    activate_account(driver, email)
    return email




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


class TestApplicationEndToEnd(unittest.TestCase):
    def setUp(self):
        self.driver = setup_driver()

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
            if self.email is not None:
                email = self.email
                dbmanager = DatabaseManager()
                dbname = dbmanager.delete_organization_all_details(email.lower())
                couchwrapper = CouchHttpWrapper()
                couchwrapper.deleteDb(dbname)
        except TypeError as e:
            pass

        teardown_driver(self.driver)


    def set_organization_number(self):
        dbmanager = DatabaseManager()
        organization_sms_tel_number = get_epoch_last_ten_digit()
        dbmanager.set_sms_telephone_number(organization_sms_tel_number, self.email.lower())
        return organization_sms_tel_number

    def do_org_registartion(self):
        registration_confirmation_page, self.email = register_and_get_email(self.driver)
        self.assertEquals(registration_confirmation_page.registration_success_message(),
                          fetch_(SUCCESS_MESSAGE, from_(REGISTRATION_DATA_FOR_SUCCESSFUL_REGISTRATION)))
        activate_account(self.driver, self.email.lower())
        return self.set_organization_number()

    def do_login(self):
        global_navigation = do_login(self.driver, self.email, REGISTRATION_PASSWORD)
        self.assertEqual(global_navigation.welcome_message(), "Welcome Mickey!")
        return global_navigation

    def add_subject_type(self, create_project_page, entity_type):
        add_subject_type_page = AddSubjectTypePage(self.driver)
        add_subject_type_page.click_on_accordian_link()
        add_subject_type_page.add_entity_type_with(entity_type)
        self.assertEqual(create_project_page.get_selected_subject(), entity_type.lower())

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
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully()
        return project_overview_page.get_project_title()

    def send_sms(self, organization_sms_tel_number, sms):
        sms_tester_page = SMSTesterPage(self.driver)
        sms_tester_data = sms
        sms_tester_data[RECEIVER] = str(organization_sms_tel_number)
        sms_tester_page.send_sms_with(sms_tester_data)
        self.assertIn(fetch_(SUCCESS_MESSAGE, from_(sms_tester_data)), sms_tester_page.get_response_message())
        return sms_tester_page

    def verify_submission(self, sms_log, project_name):
        global_navigation = GlobalNavigationPage(self.driver)
        view_all_project_page = global_navigation.navigate_to_view_all_project_page()
        project_overview_project = view_all_project_page.navigate_to_project_overview_page(project_name)
        data_page = project_overview_project.navigate_to_data_page()
        submission_log_page = data_page.navigate_to_all_data_record_page()
        self.assertRegexpMatches(submission_log_page.get_submission_message(sms_log),
                                 fetch_(SUBMISSION, from_(sms_log)))

    def verify_individual_report_project_creation(self):
        global_navigation = GlobalNavigationPage(self.driver)
        dashboard_page = global_navigation.navigate_to_dashboard_page()
        create_questionnaire_options_page = dashboard_page.navigate_to_create_project_page()

        create_questionnaire_page = create_questionnaire_options_page.select_blank_questionnaire_creation_option()
        create_questionnaire_page.create_questionnaire_with(VALID_DATA_FOR_PROJECT,QUESTIONNAIRE_DATA)


        #create_project_page.select_report_type(VALID_DATA_FOR_PROJECT)
        #self.add_subject_type(create_project_page, VALID_SUBJECT_TYPE2[ENTITY_TYPE])
        #self.add_subject_type(create_project_page, VALID_SUBJECT_TYPE1[ENTITY_TYPE])
        #create_questionnaire_page = self.create_project(create_project_page)
        #self.project_name = self.create_questionnaire(create_questionnaire_page)

        #create_questionnaire_page.create_questionnaire_with(QUESTIONNAIRE_DATA)
        index = 1
        for question in fetch_(QUESTIONS, from_(QUESTIONNAIRE_DATA)):
            question_link_text = fetch_(QUESTION, from_(question))
            self.assertEquals(create_questionnaire_page.get_question_link_text(index), question_link_text)
            index += 1
        project_overview_page = create_questionnaire_page.save_and_create_project_successfully()
        self.project_name = project_overview_page.get_project_title()


    def add_subject(self):
        global_navigation = GlobalNavigationPage(self.driver)
        global_navigation.navigate_to_all_subject_page()
        all_subject_type_page = AllSubjectTypePage(self.driver)
        add_subject_page = all_subject_type_page.add_new_subject_type("Gaming").select_subject_type("Gaming")\
            .navigate_to_register_subject_page()
        add_subject_page.add_subject_with(VALID_DATA_FOR_SUBJECT_REG)
        add_subject_page.submit_subject()
        self.assertIn(fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_FOR_SUBJECT_REG)), add_subject_page.get_flash_message())

    def add_edit_datasender(self):
        global_navigation = GlobalNavigationPage(self.driver)
        all_data_sender_page = global_navigation.navigate_to_all_data_sender_page()
        add_data_sender_page = all_data_sender_page.navigate_to_add_a_data_sender_page()
        email = generate_random_email_id()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_WITH_EMAIL, email=email)
        success_msg = add_data_sender_page.get_success_message()
        self.assertIn(fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_WITH_EMAIL)), success_msg)
        add_data_sender_page.navigate_to_datasender_page()
        all_data_sender_page = AllDataSendersPage(self.driver)


        rep_id = success_msg.replace(VALID_DATA_WITH_EMAIL[SUCCESS_MESSAGE], '')
        all_data_sender_page.select_a_data_sender_by_id(rep_id)

        all_data_sender_page.select_edit_action()
        time.sleep(2)
        edit_datasender_page = AddDataSenderPage(self.driver)
        edit_datasender_page.enter_data_sender_details_from(VALID_DATA_WITH_EMAIL_FOR_EDIT)
        self.assertRegexpMatches(edit_datasender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(VALID_DATA_WITH_EMAIL_FOR_EDIT)))

        edit_datasender_page.navigate_to_datasender_page()
        all_data_sender_page = AllDataSendersPage(self.driver)
        all_data_sender_page.associate_datasender_to_projects(rep_id, [self.project_name])
        return email

    def verify_admin_present_in_my_datasenders_page(self):
        global_navigation = GlobalNavigationPage(self.driver)
        all_project_page=global_navigation.navigate_to_view_all_project_page()
        project_overview_page=all_project_page.navigate_to_project_overview_page(self.project_name)
        my_datasenders_page=project_overview_page.navigate_to_datasenders_page()
        my_datasenders_page.search_with(self.email)
        self.assertTrue(
            self.driver.is_element_present(my_datasenders_page.get_checkbox_selector_for_datasender_row(1)))


    def verify_submission_via_sms(self, organization_sms_tel_number):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        VALID_DATA_FOR_SMS[SENDER] = VALID_DATA_WITH_EMAIL[MOBILE_NUMBER]
        self.send_sms(organization_sms_tel_number, VALID_DATA_FOR_SMS)
        self.driver.go_to(DATA_WINNER_DASHBOARD_PAGE)
        self.verify_submission(SMS_DATA_LOG, self.project_name)

    def verify_submission_via_web(self, ds_email):
        self.driver.go_to(LOGOUT)
        user = User.objects.get(username=ds_email)
        token = default_token_generator.make_token(user)
        self.driver.go_to(url(DS_ACTIVATION_URL % (int_to_base36(user.id), token)))
        activation_page = ResetPasswordPage(self.driver)
        activation_page.type_same_password(NEW_PASSWORD)
        activation_page.click_submit()
        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Data Submission")
        self.assertEqual(self.driver.get_title(), "Data Submission")
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with({USERNAME: ds_email, PASSWORD: NEW_PASSWORD})
        data_sender_page = DataSenderPage(self.driver)
        submission_page = data_sender_page.send_in_data()
        submission_page.fill_and_submit_answer(WEB_ANSWERS)
        self.driver.go_to(LOGOUT)
        self.do_login()
        self.verify_submission(WEB_ANSWER_LOG, self.project_name)

    def admin_edit_delete_submissions(self):
        submission_log_page = SubmissionLogPage(self.driver)
        submission_log_page.search(fetch_(ANSWER, WEB_ANSWERS[5]))
        submission_log_page.check_submission_by_row_number(1)
        submission_log_page.choose_on_dropdown_action(EDIT_BUTTON)

        submission_page = WebSubmissionPage(self.driver)
        submission_page.fill_and_submit_answer(EDITED_WEB_ANSWERS)
        self.verify_submission(EDITED_WEB_ANSWER_LOG, self.project_name)

        submission_log_page.check_all_submissions()
        submission_log_page.choose_on_dropdown_action(DELETE_BUTTON)
        warning_dialog = WarningDialog(self.driver)
        warning_dialog.confirm()
        submission_log_page.wait_for_table_data_to_load()
        self.assertTrue(submission_log_page.empty_help_text())

    def add_edit_delete_subject(self):
        add_subject_page = AddSubjectPage(self.driver)
        add_subject_page.add_subject_with(VALID_DATA_FOR_SUBJECT)
        add_subject_page.submit_subject()
        message = fetch_(SUCCESS_MESSAGE, from_(VALID_DATA_FOR_SUBJECT))
        flash_message = add_subject_page.get_flash_message()
        self.assertIn(message, flash_message)
        subject_short_code = flash_message.replace(message, '')

        add_subject_page.navigate_to_subject_list()
        all_subjects_list_page = AllSubjectsListPage(self.driver)
        all_subjects_list_page.select_subject_by_id(subject_short_code)
        edit_subject_page = all_subjects_list_page.click_edit_action_button()
        edit_subject_page.add_subject_with(VALID_DATA_FOR_EDIT)
        edit_subject_page.submit_subject()
        self.assertEquals(edit_subject_page.get_flash_message(), VALID_DATA_FOR_EDIT[SUCCESS_MESSAGE])

        edit_subject_page.navigate_to_subject_list()
        all_subjects_page = AllSubjectsListPage(self.driver)
        all_subjects_page.select_subject_by_id(subject_short_code)
        all_subjects_page.click_delete_action_button()
        self.driver.find(CONFIRM_DELETE).click()
        self.assertEquals(all_subjects_page.get_successfully_deleted_message(), 'Subject(s) successfully deleted.')
        self.assertFalse(all_subjects_page.is_subject_present(subject_short_code))

    def delete_project(self):
        global_navigation = GlobalNavigationPage(self.driver)
        project_page = global_navigation.navigate_to_view_all_project_page()
        self.assertTrue(project_page.is_project_present(self.project_name))

        project_page.delete_project(self.project_name)
        self.assertFalse(project_page.is_project_present(self.project_name))

    def verify_summary_report_project_creation(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css('#global_dashboard_link'))
        global_navigation_page = GlobalNavigationPage(self.driver)
        dashboard_page = global_navigation_page.navigate_to_dashboard_page()
        create_project_page = dashboard_page.navigate_to_create_project_page()
        create_project_page.create_project_with(VALID_SUMMARY_REPORT_DATA)
        create_project_page.continue_create_project()
        questionnaire_page = CreateQuestionnairePage(self.driver)
        overview_page = questionnaire_page.save_and_create_project_successfully()
        self.summary_project_name = overview_page.get_project_title()
        self.summary_project_questionnaire_code = overview_page.get_questionnaire_code()
        return overview_page


    @attr('smoke')
    def test_end_to_end(self):
        self.email = None
        organization_sms_tel_number = self.do_org_registartion()
        self.verify_individual_report_project_creation()
        self.add_subject()
        self.add_edit_delete_subject()
        ds_email = self.add_edit_datasender()
        self.verify_admin_present_in_my_datasenders_page()
        self.verify_submission_via_sms(organization_sms_tel_number)
        self.verify_submission_via_web(ds_email)
        self.admin_edit_delete_submissions()
        time.sleep(2)
        self.delete_project()

        #project_overview_page = self.verify_summary_report_project_creation()
        #project_overview_page.navigate_to_web_questionnaire_page().fill_and_submit_answer(ANSWER_FOR_SUMMARY_PROJECT)
        #self.verify_submission(SUMMARY_DATA_LOG, self.summary_project_name)