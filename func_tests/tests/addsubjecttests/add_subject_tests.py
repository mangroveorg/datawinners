# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from nose.plugins.attrib import attr

from framework.base_test import teardown_driver, HeadlessRunnerTest
from framework.utils.data_fetcher import fetch_, from_
from pages.allsubjectspage.add_subject_locator import UNIQUE_ID_TB
from pages.loginpage.login_page import LoginPage, login
from pages.allsubjectspage.add_subject_page import AddSubjectPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_ADD_SUBJECT, LOGOUT
from tests.logintests.login_data import DATA_SENDER_CREDENTIALS
from tests.addsubjecttests.add_subject_data import *
from tests.utils import get_subject_short_code


class TestAddSubject(HeadlessRunnerTest):
    @classmethod
    def setUpClass(cls):
        HeadlessRunnerTest.setUpClass()
        login(cls.driver)
        cls.add_subjects_url = DATA_WINNER_ADD_SUBJECT + "clinic/?web_view=True"

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)


    @attr('functional_test')
    def test_addition_of_subject_with_existing_data(self):
        self.driver.go_to(self.add_subjects_url)
        add_subject_page = AddSubjectPage(self.driver)
        add_subject_page.add_subject_with(EXISTING_SHORT_CODE)
        short_name = fetch_(SUB_UNIQUE_ID, from_(EXISTING_SHORT_CODE))
        self.driver.find_text_box(UNIQUE_ID_TB).enter_text(short_name)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(EXISTING_SHORT_CODE))
        self.assertEqual(add_subject_page.get_error_message(), message)

    @attr('functional_test')
    def test_addition_of_subject_with_auto_generate_false(self):
        self.driver.go_to(self.add_subjects_url)
        add_subject_page = AddSubjectPage(self.driver)
        add_subject_page.add_subject_with(SUBJECT_DATA_WITHOUT_UNIQUE_ID)
        add_subject_page.submit_subject()
        flash_message = add_subject_page.get_flash_message()
        message = fetch_(SUCCESS_MSG, from_(SUBJECT_DATA_WITHOUT_UNIQUE_ID))
        message = message % get_subject_short_code(flash_message)
        self.assertRegexpMatches(flash_message, message)

    def assertErrorMessage(self, add_subject_page, message):
        actual_message = add_subject_page.get_error_message()
        self.assertTrue(message in actual_message)

    @attr('functional_test')
    def test_addition_of_subject_with_invalid_data(self):
        self.driver.go_to(self.add_subjects_url)
        add_subject_page = AddSubjectPage(self.driver)

        add_subject_page.add_subject_with(WITHOUT_LOCATION_NAME)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(WITHOUT_LOCATION_NAME))
        self.assertRegexpMatches(add_subject_page.get_error_message(), message)
        a = self.driver.switch_to_active_element()
        self.assertEqual(a.get_attribute("id"), "id_q3")

        add_subject_page.add_subject_with(WITHOUT_GPS)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(WITHOUT_GPS))
        self.assertRegexpMatches(add_subject_page.get_error_message(), message)

        add_subject_page.add_subject_with(INVALID_LATITUDE_GPS)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(INVALID_LATITUDE_GPS))
        self.assertErrorMessage(add_subject_page, message)

        add_subject_page.add_subject_with(INVALID_LONGITUDE_GPS)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(INVALID_LONGITUDE_GPS))
        self.assertErrorMessage(add_subject_page, message)

        add_subject_page.add_subject_with(INVALID_GPS_AND_PHONE_NUMBER)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(INVALID_GPS_AND_PHONE_NUMBER))
        self.assertErrorMessage(add_subject_page, message)

        add_subject_page.add_subject_with(WITH_UNICODE_IN_GPS_AND_INVALID_PHONE_NUMBER)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(WITH_UNICODE_IN_GPS_AND_INVALID_PHONE_NUMBER))
        self.assertErrorMessage(add_subject_page, message)

        add_subject_page.add_subject_with(CLINIC_WITH_INVALID_UID)
        add_subject_page.submit_subject()
        message = fetch_(ERROR_MSG, from_(CLINIC_WITH_INVALID_UID))
        self.assertRegexpMatches(message, add_subject_page.get_error_message())

    @attr('functional_test')
    def test_cancel_link_should_be_available_for_datasender(self):
        self.driver.go_to(LOGOUT)
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(DATA_SENDER_CREDENTIALS)

        self.driver.go_to(self.add_subjects_url)

        self.assertRegexpMatches((AddSubjectPage(self.driver)).get_cancel_url(), "/alldata/")