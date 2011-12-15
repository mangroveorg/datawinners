# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr
from framework.base_test import BaseTest
from pages.loginpage.login_page import LoginPage
from pages.addsubjectpage.add_subject_page import AddSubjectPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ADD_SUBJECT
from tests.logintests.login_data import VALID_CREDENTIALS
from tests.addsubjecttests.add_subject_data import *


class TestAddSubject(BaseTest):
    def prerequisites_of_add_subject(self):
        # doing successful login with valid credentials
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)
        self.driver.go_to(DATA_WINNER_ADD_SUBJECT)
        return AddSubjectPage(self.driver)

    @attr('functional_test', 'smoke')
    def test_successful_addition_of_subject(self):
        """
        Function to test the successful addition_of_subject with given
        details
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.successfully_add_subject_with(VALID_DATA)
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_existing_data(self):
        """
        Function to test the addition_of_subject with existing short code
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.add_subject_with(EXISTING_SHORT_CODE)
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_auto_generate_false(self):
        """
        Function to test the addition_of_subject with auto generate false
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.successfully_add_subject_with(AUTO_GENERATE_FALSE)
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_without_location_name(self):
        """
        Function to test the addition_of_subject without location name
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.successfully_add_subject_with(WITHOUT_LOCATION_NAME)
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_without_gps(self):
        """
        Function to test the addition_of_subject without GPS
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.successfully_add_subject_with(WITHOUT_GPS)
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_latitude_gps(self):
        """
        Function to test the addition_of_subject with invalid latitude
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.add_subject_with(INVALID_LATITUDE_GPS)
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_longitude_gps(self):
        """
        Function to test the addition_of_subject with invalid latitude
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.add_subject_with(INVALID_LONGITUDE_GPS)
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_gps(self):
        """
        Function to test the addition_of_subject with invalid gps
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.add_subject_with(INVALID_GPS)
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_invalid_gps_with_comma(self):
        """
        Function to test the addition_of_subject with invalid gps with comma
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.add_subject_with(INVALID_GPS_WITH_COMMA)
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_unicode_in_gps(self):
        """
        Function to test the addition_of_subject with unicode in GPS
        """
        add_subject_page = self.prerequisites_of_add_subject()
        message = add_subject_page.add_subject_with(WITH_UNICODE_IN_GPS)
        self.assertEqual(add_subject_page.get_error_message(), message)
