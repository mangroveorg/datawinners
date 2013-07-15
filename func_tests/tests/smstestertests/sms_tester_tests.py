# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from nose.plugins.attrib import attr
from framework.base_test import setup_driver, teardown_driver
from framework.utils.data_fetcher import fetch_, from_
from pages.smstesterpage.sms_tester_page import SMSTesterPage
from testdata.test_data import DATA_WINNER_SMS_TESTER_PAGE
from tests.smstestertests.sms_tester_data import *


@attr('suit_3')
class TestSMSTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = setup_driver()
        cls.driver.go_to(DATA_WINNER_SMS_TESTER_PAGE)
        cls.sms_tester_page = SMSTesterPage(cls.driver)

    @classmethod
    def tearDownClass(cls):
        teardown_driver(cls.driver)

    @attr('functional_test', 'smoke')
    def test_successful_sms_submission(self):
        self.sms_tester_page.send_sms_with(VALID_DATA)
        self.assertEqual(self.sms_tester_page.get_response_message(), fetch_(SUCCESS_MESSAGE, from_(VALID_DATA)))

    @attr('functional_test')
    def test_sms_player_without_entering_data(self):
        self.sms_tester_page.send_sms_with(BLANK_FIELDS)
        self.assertEqual(self.sms_tester_page.get_error_message(), fetch_(ERROR_MSG, from_(BLANK_FIELDS)))

    @attr('functional_test')
    def test_sms_player_for_exceeding_word_length(self):
        self.sms_tester_page.send_sms_with(EXCEED_NAME_LENGTH)
        self.assertEqual(self.sms_tester_page.get_response_message(), fetch_(ERROR_MSG, from_(EXCEED_NAME_LENGTH)))

    @attr('functional_test')
    def test_sms_player_for_plus_in_the_beginning(self):
        self.sms_tester_page.send_sms_with(PLUS_IN_THE_BEGINNING)
        self.assertEqual(self.sms_tester_page.get_response_message(), fetch_(ERROR_MSG, from_(PLUS_IN_THE_BEGINNING)))

    @attr('functional_test')
    def test_sms_player_for_unregistered_from_number(self):
        self.sms_tester_page.send_sms_with(UNREGISTERED_FROM_NUMBER)
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(ERROR_MSG, from_(UNREGISTERED_FROM_NUMBER)))

    @attr('functional_test')
    def test_sms_player_for_addition_of_data_sender(self):
        """
        Function to test the registration of the reporter using sms submission with registered number
        """
        self.sms_tester_page.send_sms_with(REGISTER_DATA_SENDER)
        self.assertRegexpMatches(self.sms_tester_page.get_response_message(),
                                 fetch_(SUCCESS_MESSAGE, from_(REGISTER_DATA_SENDER)))

    @attr('functional_test')
    def test_sms_player_for_addition_of_data_sender_from_unknown_number(self):
        self.sms_tester_page.send_sms_with(REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER)
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(ERROR_MSG, from_(REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER)))

    @attr('functional_test')
    def test_sms_player_for_registration_of_new_subject(self):
        self.sms_tester_page.send_sms_with(REGISTER_NEW_SUBJECT)
        self.assertTrue(
            fetch_(SUCCESS_MESSAGE, from_(REGISTER_NEW_SUBJECT)) in self.sms_tester_page.get_response_message())

    @attr('functional_test')
    def test_sms_player_for_registration_of_existing_subject_short_code(self):
        self.sms_tester_page.send_sms_with(REGISTER_EXISTING_SUBJECT_SHORT_CODE)
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(ERROR_MSG, from_(REGISTER_EXISTING_SUBJECT_SHORT_CODE)))

    @attr('functional_test')
    def test_sms_player_for_registration_with_invalid_geo_code(self):
        self.sms_tester_page.send_sms_with(REGISTER_INVALID_GEO_CODE)
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(ERROR_MSG, from_(REGISTER_INVALID_GEO_CODE)))

    @attr('functional_test')
    def test_sms_player_for_only_questionnaire_code(self):
        self.sms_tester_page.send_sms_with(ONLY_QUESTIONNAIRE_CODE)
        self.assertEqual(self.sms_tester_page.get_response_message(), fetch_(ERROR_MSG, from_(ONLY_QUESTIONNAIRE_CODE)))

    @attr('functional_test')
    def test_sms_player_for_wrong_number_of_arg(self):
        self.sms_tester_page.send_sms_with(WRONG_NUMBER_OF_ARGS)
        self.assertEqual(self.sms_tester_page.get_response_message(), fetch_(ERROR_MSG, from_(WRONG_NUMBER_OF_ARGS)))

    @attr('functional_test')
    def test_sms_player_for_unregistered_subject_and_invalid_geo_code(self):
        self.sms_tester_page.send_sms_with(UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA)
        self.assertEqual(self.sms_tester_page.get_response_message(),
                         fetch_(ERROR_MSG, from_(UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA)))
   