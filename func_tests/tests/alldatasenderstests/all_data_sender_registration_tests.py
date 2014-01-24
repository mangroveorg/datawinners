import unittest
import time

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from south.tests import skiptest
from framework.utils.common_utils import by_css

from framework.utils.data_fetcher import fetch_, from_
from framework.base_test import setup_driver, teardown_driver
from pages.adddatasenderspage.add_data_senders_locator import NAME_TB, MOBILE_NUMBER_TB, COMMUNE_TB, GPS_TB
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from pages.loginpage.login_page import LoginPage
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_CREATE_DATA_SENDERS, DATA_WINNER_ALL_DATA_SENDERS_PAGE
from tests.logintests.login_data import VALID_CREDENTIALS, USERNAME, PASSWORD
from tests.alldatasenderstests.add_data_senders_data import *
from pages.globalnavigationpage.global_navigation_page import GlobalNavigationPage

@skiptest # Skipped since datasender registration form is now a popup and the page current page is testing is no longer used
class TestAllDataSenderRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    def setUp(self):
        TestAllDataSenderRegistration.driver.refresh()
        self.driver.go_to(DATA_WINNER_CREATE_DATA_SENDERS)
        self.current_page = AddDataSenderPage(self.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    def login_with_created_datasenders_account(self, email):
        global_navigation = GlobalNavigationPage(self.driver)
        global_navigation.sign_out()
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        data_sender_credentials = {USERNAME: email, PASSWORD: "test123"}
        login_page = LoginPage(self.driver)
        login_page.login_with(data_sender_credentials)
        message = global_navigation.welcome_message()
        return message

    @attr('functional_test')
    def test_successful_addition_and_editing_of_data_sender(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA)
        success_msg = add_data_sender_page.get_success_message()
        self.assertRegexpMatches(success_msg, fetch_(SUCCESS_MSG, from_(VALID_DATA)))
        rep_id = self._parse(success_msg)
        all_data_senders_page = AllDataSendersPage(self.driver)
        all_data_senders_page.load()
        all_data_senders_page.search_with(rep_id)
        all_data_senders_page.select_a_data_sender_by_id(rep_id)
        all_data_senders_page.select_edit_action()
        self.current_page.enter_data_sender_details_from(VALID_EDIT_DATA)
        self.assertRegexpMatches(self.current_page.get_success_message(), fetch_(SUCCESS_MSG, from_(VALID_EDIT_DATA)))


    @attr('functional_test')
    def test_addition_of_data_sender_without_email_address(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.select_web_device()
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_WITHOUT_EMAIL)

        self.assertRegexpMatches(add_data_sender_page.get_error_message(),
                                 fetch_(ERROR_MSG, from_(VALID_DATA_WITHOUT_EMAIL)))

    @attr('functional_test')
    def test_addition_of_data_sender_without_entering_data(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(BLANK_FIELDS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(BLANK_FIELDS)))
        a = self.driver.switch_to_active_element()
        self.assertEqual(a.get_attribute("id"), u"id_name")

    @attr('functional_test')
    def test_addition_of_data_sender_with_existing_data(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(EXISTING_DATA)

        time.sleep(1)
        self.assertEqual(add_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(EXISTING_DATA)))

    @attr('functional_test')
    def test_addition_of_data_sender_without_location_name(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(WITHOUT_LOCATION_NAME)
        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(WITHOUT_LOCATION_NAME)))

    @attr('functional_test')
    def test_addition_of_data_sender_without_gps(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(WITHOUT_GPS)
        self.assertRegexpMatches(add_data_sender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(WITHOUT_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_invalid_gps(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(INVALID_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_invalid_latitude_gps(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_LATITUDE_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(INVALID_LATITUDE_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_invalid_longitude_gps(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_LONGITUDE_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(INVALID_LONGITUDE_GPS)))

    @attr('functional_test')
    def test_addition_of_data_sender_with_unicode_in_gps(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(WITH_UNICODE_IN_GPS)
        self.assertEqual(add_data_sender_page.get_error_message(), fetch_(ERROR_MSG, from_(WITH_UNICODE_IN_GPS)))

    @SkipTest
    def test_addition_of_data_sender_with_invalid_gps_with_comma(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(INVALID_GPS_WITH_COMMA)
        self.assertEqual(add_data_sender_page.get_error_message(),
                         fetch_(ERROR_MSG, from_(INVALID_GPS_WITH_COMMA)))

    @attr('functional_test')
    def test_add_datasender_with_long_uid(self):
        add_data_sender_page = self.current_page
        self.driver.find(by_css("#generate_id")).click()
        self.driver.find_text_box(by_css("#id_short_code")).enter_text("rep012345678901234567891")
        short_code = self.driver.find(by_css("#id_short_code")).get_attribute('value')
        self.assertEquals(len(short_code), 12)


    def assert_fields_are_populated_properly_in_edit_page(self, valid_registration_data):
        self.assertEquals(fetch_(NAME, from_(valid_registration_data)),
                          self.driver.find_text_box(NAME_TB).get_attribute('value'))
        self.assertEquals(fetch_(MOBILE_NUMBER, from_(valid_registration_data)),
                          self.driver.find_text_box(MOBILE_NUMBER_TB).get_attribute('value'))
        self.assertEqual(fetch_(COMMUNE, from_(valid_registration_data)),
                         self.driver.find_text_box(COMMUNE_TB).get_attribute('value'))
        self.assertEqual(fetch_(GPS, from_(valid_registration_data)),
                         self.driver.find_text_box(GPS_TB).get_attribute('value'))

    @attr('functional_test')
    def test_edit_datasender_should_populate_all_fields_properly(self):
        add_data_sender_page = self.current_page
        add_data_sender_page.enter_data_sender_details_from(VALID_DATA_WITH_EMAIL)
        success_msg = self.current_page.get_success_message()
        rep_id = self._parse(success_msg)
        self.assertRegexpMatches(success_msg,
                                 fetch_(SUCCESS_MSG, from_(VALID_DATA_WITH_EMAIL)))

        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_datasender_page = AllDataSendersPage(self.driver)
        edit_datasender_page = all_datasender_page.edit_datasender(rep_id)

        self.assert_fields_are_populated_properly_in_edit_page(VALID_DATA_WITH_EMAIL)

        edit_datasender_page.enter_data_sender_details_from(VALID_DATA_WITH_EMAIL_EDITED)
        self.assertRegexpMatches(edit_datasender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(VALID_DATA_WITH_EMAIL_EDITED)))

        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_datasender_page = AllDataSendersPage(self.driver)
        all_datasender_page.edit_datasender(rep_id)

        self.assert_fields_are_populated_properly_in_edit_page(VALID_DATA_WITH_EMAIL_EDITED)

     # @attr('functional_test')
#     def test_should_uncheck_reporter_id_checkbox_if_user_has_given_id(self):
#         self.driver.go_to(DATA_WINNER_CREATE_DATA_SENDERS)
#         add_data_sender_page = AddDataSenderPage(self.driver)
#         self.assertTrue(add_data_sender_page.unique_id_check_box_is_checked())
#         add_data_sender_page.enter_data_sender_details_from(INVALID_MOBILE_NUMBER_DATA, "DS040")
#         time.sleep(1)
#         self.assertFalse(add_data_sender_page.unique_id_check_box_is_checked())
#         self.assertTrue(add_data_sender_page.unique_id_field_is_enabled())
#

    def _parse(self, message):
            return message.split(' ')[-1]




