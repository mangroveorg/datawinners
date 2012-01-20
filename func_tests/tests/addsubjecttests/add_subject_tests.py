# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.loginpage.login_page import LoginPage
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ADD_SUBJECT
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.addsubjecttests.add_subject_data import *


class TestAddSubject(BaseTest):
    def prerequisites_of_add_subject(self, subject_data):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        entity_type = fetch_(ENTITY_TYPE, from_(subject_data))
        self.driver.go_to(DATA_WINNER_ADD_SUBJECT + entity_type)
        return AddSubjectPage(self.driver)

    @attr('functional_test', 'smoke')
    def test_successful_addition_of_subject(self):
        """
        Function to test the successful addition_of_subject with given
        details
        """
        add_subject_page = self.prerequisites_of_add_subject(VALID_DATA)
        add_subject_page.add_subject_with(VALID_DATA)
        add_subject_page.submit_subject()
        message = VALID_DATA[ERROR_MSG]
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_existing_data(self):
        """
        Function to test the addition_of_subject with existing short code
        """
        add_subject_page = self.prerequisites_of_add_subject(EXISTING_SHORT_CODE)
        add_subject_page.add_subject_with(EXISTING_SHORT_CODE)
        add_subject_page.submit_subject()
        message = EXISTING_SHORT_CODE[ERROR_MSG]
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_auto_generate_false(self):
        """
        Function to test the addition_of_subject with auto generate false
        """
        add_subject_page = self.prerequisites_of_add_subject(AUTO_GENERATE_FALSE)
        add_subject_page.successfully_add_subject_with(AUTO_GENERATE_FALSE)
        add_subject_page.submit_subject()
        message = AUTO_GENERATE_FALSE[ERROR_MSG]
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_without_location_name(self):
        """
        Function to test the addition_of_subject without location name
        """
        add_subject_page = self.prerequisites_of_add_subject(WITHOUT_LOCATION_NAME)
        add_subject_page.successfully_add_subject_with(WITHOUT_LOCATION_NAME)
        add_subject_page.submit_subject()
        message = WITHOUT_LOCATION_NAME[ERROR_MSG]
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_without_gps(self):
        """
        Function to test the addition_of_subject without GPS
        """
        add_subject_page = self.prerequisites_of_add_subject(WITHOUT_GPS)
        add_subject_page.successfully_add_subject_with(WITHOUT_GPS)
        add_subject_page.submit_subject()
        message = WITHOUT_GPS[ERROR_MSG]
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_latitude_gps(self):
        """
        Function to test the addition_of_subject with invalid latitude
        """
        add_subject_page = self.prerequisites_of_add_subject(INVALID_LATITUDE_GPS)
        add_subject_page.add_subject_with(INVALID_LATITUDE_GPS)
        add_subject_page.submit_subject()
        message = INVALID_LATITUDE_GPS[ERROR_MSG]
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_longitude_gps(self):
        """
        Function to test the addition_of_subject with invalid latitude
        """
        add_subject_page = self.prerequisites_of_add_subject(INVALID_LONGITUDE_GPS)
        add_subject_page.add_subject_with(INVALID_LONGITUDE_GPS)
        add_subject_page.submit_subject()
        message = INVALID_LONGITUDE_GPS[ERROR_MSG]
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_gps(self):
        """
        Function to test the addition_of_subject with invalid gps
        """
        add_subject_page = self.prerequisites_of_add_subject(INVALID_GPS)
        add_subject_page.add_subject_with(INVALID_GPS)
        add_subject_page.submit_subject()
        message = INVALID_GPS[ERROR_MSG]
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_gps_with_comma(self):
        """
        Function to test the addition_of_subject with invalid gps with comma
        """
        add_subject_page = self.prerequisites_of_add_subject(INVALID_GPS_WITH_COMMA)
        add_subject_page.add_subject_with(INVALID_GPS_WITH_COMMA)
        add_subject_page.submit_subject()
        message = INVALID_GPS_WITH_COMMA[ERROR_MSG]
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_unicode_in_gps(self):
        """
        Function to test the addition_of_subject with unicode in GPS
        """
        add_subject_page = self.prerequisites_of_add_subject(WITH_UNICODE_IN_GPS)
        add_subject_page.add_subject_with(WITH_UNICODE_IN_GPS)
        add_subject_page.submit_subject()
        message = WITH_UNICODE_IN_GPS[ERROR_MSG]
        self.assertEqual(add_subject_page.get_error_message(), message)
