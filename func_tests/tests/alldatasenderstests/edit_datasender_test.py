import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.adddatasenderspage.add_data_senders_locator import NAME_TB, MOBILE_NUMBER_TB, COMMUNE_TB, GPS_TB
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_page import AllDataSendersPage
from pages.loginpage.login_page import LoginPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE, DATA_WINNER_CREATE_DATA_SENDERS, DATA_WINNER_ALL_DATA_SENDERS_PAGE
from tests.alldatasenderstests.add_data_senders_data import NAME, MOBILE_NUMBER, COMMUNE, GPS, VALID_DATA_WITH_EMAIL, SUCCESS_MSG, VALID_EDIT_DATA
from tests.logintests.login_data import VALID_CREDENTIALS


@attr('suit_1')
class TestAllDataSenderEdit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(cls.driver)
        login_page.do_successful_login_with(VALID_CREDENTIALS)

    def setUp(self):
        TestAllDataSenderEdit.driver.refresh()
        self.driver.go_to(DATA_WINNER_CREATE_DATA_SENDERS)
        self.current_page = AddDataSenderPage(self.driver)

    def tearDown(self):
        import sys

        exception_info = sys.exc_info()
        if exception_info != (None, None, None):
            import os

            if not os.path.exists("screenshots"):
                os.mkdir("screenshots")
            self.driver.get_screenshot_as_file(
                "screenshots/screenshot-%s-%s.png" % (self.__class__.__name__, self._testMethodName))

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)


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
        success_msg = add_data_sender_page.get_success_message()
        rep_id = success_msg.split(' ')[-1]
        self.assertRegexpMatches(success_msg,
                                 fetch_(SUCCESS_MSG, from_(VALID_DATA_WITH_EMAIL)))

        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_datasender_page = AllDataSendersPage(self.driver)
        edit_datasender_page = all_datasender_page.edit_datasender(rep_id)

        self.assert_fields_are_populated_properly_in_edit_page(VALID_DATA_WITH_EMAIL)

        edit_datasender_page.enter_data_sender_details_from(VALID_EDIT_DATA)
        self.assertRegexpMatches(edit_datasender_page.get_success_message(),
                                 fetch_(SUCCESS_MSG, from_(VALID_EDIT_DATA)))

        self.driver.go_to(DATA_WINNER_ALL_DATA_SENDERS_PAGE)
        all_datasender_page = AllDataSendersPage(self.driver)
        all_datasender_page.edit_datasender(rep_id)

        self.assert_fields_are_populated_properly_in_edit_page(VALID_EDIT_DATA)