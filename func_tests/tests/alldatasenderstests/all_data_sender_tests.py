# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_SMS_TESTER_PAGE, DATA_WINNER_CREATE_DATA_SENDERS, DATA_WINNER_ALL_DATA_SENDERS_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.alldatasenderstests.all_data_sender_data import *
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from tests.projectdatasenderstests.registered_datasenders_data import IMPORT_DATA_SENDER_TEMPLATE_FILENAME_EN, IMPORT_DATA_SENDER_TEMPLATE_FILENAME_FR
import time

@attr('suit_1')
class TestAllDataSender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        cls.page = AllDataSendersPage(cls.driver)

    def setUp(self):
        #self.driver.refresh()
        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def login(self):
        login_page = LoginPage(self.driver)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    def associate(self, all_data_sender_page):
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(ASSOCIATE_DATA_SENDER)))
        all_data_sender_page.associate_data_sender()
        all_data_sender_page.select_project(fetch_(PROJECT_NAME, from_(ASSOCIATE_DATA_SENDER)))
        all_data_sender_page.click_confirm(wait=True)

    def delete_ds(self, all_data_sender_page):
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(DELETE_DATA_SENDER)))
        all_data_sender_page.delete_data_sender()
        all_data_sender_page.click_delete(wait=True)

    def send_sms(self, sms_data, sms_tester_page):
        self.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        sms_tester_page.send_sms_with(sms_data)

    @attr('functional_tests', 'smoke')
    def test_all_data_senders_page(self):
        all_data_sender_page = self.page
        all_data_sender_page.check_links()


    @attr('functional_test', 'smoke')
    def test_successful_association_of_data_sender(self):
        """
        Function to test the successful association of DataSender with given project
        """
        all_data_sender_page = self.page
        self.associate(all_data_sender_page)
        self.assertEqual(all_data_sender_page.get_project_names(fetch_(UID, from_(ASSOCIATE_DATA_SENDER))),
                                    fetch_(PROJECT_NAME, from_(ASSOCIATE_DATA_SENDER)))

    @attr('functional_test', 'smoke')
    def test_successful_dissociation_of_data_sender(self):
        """
        Function to test the successful dissociation of DataSender with given project
        """
        all_data_sender_page = self.page
        if all_data_sender_page.get_project_names(fetch_(UID, from_(ASSOCIATE_DATA_SENDER))) == "--":
            self.associate(all_data_sender_page)
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(DISSOCIATE_DATA_SENDER)))
        all_data_sender_page.dissociate_data_sender()
        all_data_sender_page.select_project(fetch_(PROJECT_NAME, from_(DISSOCIATE_DATA_SENDER)))
        all_data_sender_page.click_confirm(wait=True)
        self.assertEqual(all_data_sender_page.get_project_names(fetch_(UID, from_(DISSOCIATE_DATA_SENDER))), "--")

    @attr('functional_test')
    def test_dissociate_ds_without_selecting_project(self):
        """
        Function to test the dissociation of DataSender without selecting project
        """
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))
        all_data_sender_page.dissociate_data_sender()
        all_data_sender_page.click_confirm()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(DISSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))

    @attr('functional_test')
    def test_associate_ds_without_selecting_project(self):
        """
        Function to test the association of DataSender without selecting project
        """
        all_data_sender_page = self.page
        all_data_sender_page.select_a_data_sender_by_id(fetch_(UID, from_(ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))
        all_data_sender_page.associate_data_sender()
        all_data_sender_page.click_confirm()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(ASSOCIATE_DS_WITHOUT_SELECTING_PROJECT)))

    @attr('functional_test')
    def test_dissociate_ds_without_selecting_ds(self):
        """
        Function to test the dissociation of DataSender without selecting datasender
        """
        all_data_sender_page = self.page
        all_data_sender_page.dissociate_data_sender()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(DISSOCIATE_DS_WITHOUT_SELECTING_DS)))

    @attr('functional_test')
    def test_associate_ds_without_selecting_ds(self):
        """
        Function to test the association of DataSender without selecting datasender
        """
        all_data_sender_page = self.page
        all_data_sender_page.associate_data_sender()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(ASSOCIATE_DS_WITHOUT_SELECTING_DS)))

    @attr('functional_test')
    def test_delete_ds_without_selecting_ds(self):
        """
        Function to test the delete data sender without selecting data sender
        """
        all_data_sender_page = self.page
        all_data_sender_page.delete_data_sender()
        self.assertEqual(all_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(DELETE_DS_WITHOUT_SELECTING_DS)))

    @attr('functional_test')
    def test_delete_data_sender_and_re_register(self):
        """
        Function to test the delete data sender without selecting data sender
        """
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
        self.login()

    @attr('functional_test')
    def test_data_sender_devices(self):
        all_data_senders_page = self.page
        self.assertTrue(all_data_senders_page.check_sms_device_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS))
        self.assertTrue(all_data_senders_page.check_web_device_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS))
        self.assertTrue(all_data_senders_page.check_smart_phone_device_by_id(DATA_SENDER_ID_WITH_WEB_ACCESS))

        self.assertTrue(all_data_senders_page.check_sms_device_by_id(DATA_SENDER_ID_WITHOUT_WEB_ACCESS))
        self.assertFalse(all_data_senders_page.check_web_device_by_id(DATA_SENDER_ID_WITHOUT_WEB_ACCESS))
        self.assertFalse(all_data_senders_page.check_smart_phone_device_by_id(DATA_SENDER_ID_WITHOUT_WEB_ACCESS))

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

