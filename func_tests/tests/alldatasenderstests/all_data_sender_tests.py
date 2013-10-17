# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
import time

from django.utils.unittest.case import SkipTest
from nose.plugins.attrib import attr

from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_locator import WEB_USER_BLOCK_EMAIL, GIVE_ACCESS_LINK
from pages.alluserspage.all_users_page import AllUsersPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_CREATE_DATA_SENDERS, DATA_WINNER_ALL_DATA_SENDERS_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.alldatasenderstests.all_data_sender_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from tests.projects.datasenderstests.registered_datasenders_data import IMPORT_DATA_SENDER_TEMPLATE_FILENAME_EN, IMPORT_DATA_SENDER_TEMPLATE_FILENAME_FR
from pages.warningdialog.warning_dialog_page import WarningDialog


@attr('suit_1')
@SkipTest
class TestAllDataSender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.page = AllDataSendersPage(cls.driver)
        cls.datasender_id_with_web_access = cls.register_datasender(VALID_DATASENDER_WITH_WEB_ACCESS)
        cls.datasender_id_without_web_access = cls.register_datasender(VALID_DATASENDER_WITHOUT_WEB_ACCESS)

    def setUp(self):
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def login(self):
        login_page = LoginPage(self.driver)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    def associate(self, all_data_sender_page, datasender_id, project_name):
        all_data_sender_page.select_a_data_sender_by_id(datasender_id)
        all_data_sender_page.associate_data_sender()
        all_data_sender_page.select_project(project_name)
        all_data_sender_page.click_confirm(wait=True)

    def dissociate(self, all_data_sender_page, datasender_id, project_name):
        all_data_sender_page.select_a_data_sender_by_id(datasender_id)
        all_data_sender_page.dissociate_data_sender()
        all_data_sender_page.select_project(project_name)
        all_data_sender_page.click_confirm(wait=True)

    def delete_ds(self, all_data_sender_page):
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(DELETE_DATA_SENDER)))
        all_data_sender_page.delete_data_sender()
        all_data_sender_page.click_delete(wait=True)

    @classmethod
    def register_datasender(cls, datasender_details):
        cls.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        add_data_sender_page = cls.page.navigate_to_add_a_data_sender_page()
        add_data_sender_page.enter_data_sender_details_from(datasender_details)

        message = add_data_sender_page.get_success_message()
        assert REGISTRATION_SUCCESS_MESSAGE_TEXT in message
        data_sender_id = _parse(message)
        return data_sender_id

    def send_sms(self, sms_data, sms_tester_page):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page.send_sms_with(sms_data)

    @attr('functional_tests')
    def test_all_data_senders_page(self):
        all_data_sender_page = self.page
        all_data_sender_page.check_links()


    @attr('functional_test')
    def test_successful_dissociation_of_data_sender(self):
        all_data_sender_page = self.page

        project_name = fetch_(PROJECT_NAME, from_(ASSOCIATE_DATA_SENDER))
        self.associate(all_data_sender_page, self.datasender_id_without_web_access, project_name)
        self.dissociate(all_data_sender_page, self.datasender_id_without_web_access, project_name)
        self.assertNotIn(project_name,all_data_sender_page.get_project_names(self.datasender_id_without_web_access))

    @attr('functional_test')
    def test_dissociate_ds_without_selecting_project(self):
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        all_data_sender_page.dissociate_data_sender()
        all_data_sender_page.click_confirm()
        self.assertEqual(all_data_sender_page.get_error_message(), ERROR_MSG_FOR_NOT_SELECTING_PROJECT)

    @attr('functional_test')
    def test_associate_ds_without_selecting_project(self):
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        all_data_sender_page.associate_data_sender()
        all_data_sender_page.click_confirm()
        self.assertEqual(all_data_sender_page.get_error_message(),ERROR_MSG_FOR_NOT_SELECTING_PROJECT)

    @SkipTest #TODO only failing on ci. need to investigate.
    @attr('functional_test')
    def test_delete_data_sender_and_re_register(self):
        all_data_sender_page = self.page
        self.delete_ds(all_data_sender_page)
        self.assertEqual(all_data_sender_page.get_delete_success_message(), DELETE_SUCCESS_TEXT)
        global_navigation = GlobalNavigationPage(self.driver)
        global_navigation.sign_out()

        sms_tester_page = SMSTesterPage(self.driver)
        self.send_sms(VALID_SMS, sms_tester_page)
        self.assertEqual(sms_tester_page.get_response_message(), SMS_ERROR_MESSAGE)

        self.login()
        self.driver.go_to(DATA_WINNER_CREATE_DATA_SENDERS)
        add_data_sender_page = AddDataSenderPage(self.driver)
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA)
        message = add_data_sender_page.get_success_message()
        self.assertRegexpMatches(message, fetch_(SUCCESS_MSG, from_(VALID_DATA)))
        self.assertNotEqual(message.split()[-1], fetch_(UID, from_(DELETE_DATA_SENDER)))
        self.driver.wait_until_modal_dismissed(10)
        global_navigation.sign_out()

        self.send_sms(VALID_SMS, sms_tester_page)
        self.assertEqual(sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, from_(VALID_SMS)))

    @attr('functional_test')
    def test_the_datasender_template_file_downloaded(self):
        all_data_sender_page = self.page
        import_lightbox = all_data_sender_page.open_import_lightbox()
        self.assertEqual(IMPORT_DATA_SENDER_TEMPLATE_FILENAME_EN, import_lightbox.get_template_filename())
        import_lightbox.close_light_box()
        all_data_sender_page.switch_language("fr")
        all_data_sender_page.open_import_lightbox()
        self.assertEqual(IMPORT_DATA_SENDER_TEMPLATE_FILENAME_FR, import_lightbox.get_template_filename())

    @attr('functional_test')
    def test_should_uncheck_reporter_id_checkbox_if_user_has_given_id(self):
        self.driver.go_to(DATA_WINNER_CREATE_DATA_SENDERS)
        add_data_sender_page = AddDataSenderPage(self.driver)
        self.assertTrue(add_data_sender_page.unique_id_check_box_is_checked())
        add_data_sender_page.enter_data_sender_details_from(INVALID_MOBILE_NUMBER_DATA, "DS040")
        time.sleep(1)
        self.assertFalse(add_data_sender_page.unique_id_check_box_is_checked())
        self.assertTrue(add_data_sender_page.unique_id_field_is_enabled())

    def add_new_user(self, user_data):
        self.driver.go_to(ALL_USERS_URL)
        all_users_page = AllUsersPage(self.driver)
        add_user_page = all_users_page.navigate_to_add_user()
        add_user_page.add_user_with(user_data)
        user_mobile_number = fetch_(MOBILE_PHONE, user_data)
        return user_mobile_number

    @attr('functional_test')
    def test_should_warn_and_not_delete_if_all_ds_selected_are_users(self):
        user_mobile_number = self.add_new_user(NEW_USER_DATA)
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        time.sleep(1)

        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_mobile(user_mobile_number)
        all_data_sender_page.delete_data_sender()
        warning = WarningDialog(self.driver)
        message = warning.get_message()
        warning.cancel()
        self.assertRegexpMatches(message, ALL_DS_TO_DELETE_ARE_USER_MSG)

    @attr('functional_test')
    def test_should_warn_that_ds_with_user_credentials_will_not_be_deleted(self):
        user_mobile_number = self.add_new_user(NEW_USER_DATA)
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        time.sleep(1)
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_mobile(user_mobile_number)
        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        all_data_sender_page.delete_data_sender()
        warning = WarningDialog(self.driver)
        message = warning.get_message()
        self.assertRegexpMatches(message, NOTIFICATION_WHILE_DELETING_USER)

    @attr('functional_test')
    def test_should_warn_delete_ds_without_note_if_ther_is_no_ds_user(self):
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        all_data_sender_page.delete_data_sender()
        warning = WarningDialog(self.driver)
        message = warning.get_message()
        self.assertNotRegexpMatches(message, NOTIFICATION_WHILE_DELETING_USER)

    @attr('functional_test')
    def test_should_check_all_checkboxes_when_checking_checkall(self):
        all_data_sender_page = self.page
        all_data_sender_page.click_checkall_checkbox()
        all_ds_count = all_data_sender_page.get_datasenders_count()
        all_checked_ds_count = all_data_sender_page.get_checked_datasenders_count()
        self.assertEqual(all_ds_count, all_checked_ds_count)

        all_data_sender_page.click_checkall_checkbox()
        all_checked_ds_count = all_data_sender_page.get_checked_datasenders_count()
        self.assertEqual(all_checked_ds_count, 0)

    @attr("functional_test")
    def test_should_load_actions_dynamically(self):
        all_data_sender_page = self.page
        all_data_sender_page.click_action_button()
        self.assert_none_selected_shown(all_data_sender_page)

        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        all_data_sender_page.click_action_button()
        self.assert_action_menu_shown(all_data_sender_page)

        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_with_web_access)
        all_data_sender_page.click_action_button()
        self.assertTrue(all_data_sender_page.is_edit_disabled())

    def assert_none_selected_shown(self, all_data_sender_page):
        self.assertFalse(all_data_sender_page.is_edit_disabled())
        self.assertTrue(all_data_sender_page.is_none_selected_shown())
        self.assertFalse(all_data_sender_page.actions_menu_shown())

    def assert_action_menu_shown(self, all_data_sender_page):
        self.assertFalse(all_data_sender_page.is_none_selected_shown())
        self.assertTrue(all_data_sender_page.actions_menu_shown())
        self.assertFalse(all_data_sender_page.is_edit_disabled())

    @attr("functional_test")
    def test_should_uncheck_checkall_when_trying_to_delete_ds_user(self):
        all_data_sender_page = self.page
        all_data_sender_page.click_checkall_checkbox()
        all_data_sender_page.delete_data_sender()
        self.assertFalse(all_data_sender_page.is_checkall_checked())

    @attr("functional_test")
    def test_should_check_checkall_when_all_cb_are_checked(self):
        all_data_sender_page = self.page
        all_data_sender_page.click_checkall_checkbox()
        self.assertTrue(all_data_sender_page.is_checkall_checked())
        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        self.assertFalse(all_data_sender_page.is_checkall_checked())
        all_data_sender_page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        self.assertTrue(all_data_sender_page.is_checkall_checked())

    def give_web_and_smartphone_access(self, all_data_senders_page):
        all_data_senders_page.give_web_access()
        email_text_box = self.driver.find_text_box(WEB_USER_BLOCK_EMAIL)
        email = generate_random_email_id()
        email_text_box.enter_text(email)
        self.driver.find(GIVE_ACCESS_LINK).click()

    @attr("functional_test")
    def test_should_able_to_give_web_and_smartphone_access(self):
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        self.assertFalse(self.page.is_web_and_smartphone_device_checkmarks_present(self.datasender_id_without_web_access))
        self.page.select_a_data_sender_by_id(self.datasender_id_without_web_access)
        self.give_web_and_smartphone_access(self.page)
        self.driver.wait_for_page_with_title(10, 'All Data Senders')
        self.driver.refresh()
        self.assertTrue(self.page.is_web_and_smartphone_device_checkmarks_present(self.datasender_id_without_web_access))

def _parse(message):
    return message.split(' ')[-1]