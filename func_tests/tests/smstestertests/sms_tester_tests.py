# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datetime import datetime

from nose.plugins.attrib import attr

from framework.utils.data_fetcher import fetch_, from_
from tests.smstestertests.sms_tester_data import *
from datawinners.tests.data import DEFAULT_TEST_ORG_ID
from datawinners.accountmanagement.models import Organization
from tests.submissionlogtests.submission_log_tests import send_sms_with


class TestSMSTester(unittest.TestCase):

    @attr('functional_test')
    def test_sms_player_for_exceeding_word_length(self):
        self.assertEqual(send_sms_with(EXCEED_NAME_LENGTH), fetch_(ERROR_MSG, from_(EXCEED_NAME_LENGTH)))

    @attr('functional_test')
    def test_sms_player_for_plus_in_the_beginning(self):
        self.assertEqual(send_sms_with(PLUS_IN_THE_BEGINNING), fetch_(ERROR_MSG, from_(PLUS_IN_THE_BEGINNING)))

    @attr('functional_test')
    def test_sms_player_for_unregistered_from_number(self):
        self.assertEqual(send_sms_with(UNREGISTERED_FROM_NUMBER),
                         fetch_(ERROR_MSG, from_(UNREGISTERED_FROM_NUMBER)))

    @attr('functional_test')
    def test_sms_player_for_addition_of_data_sender(self):
        """
        Function to test the registration of the reporter using sms submission with registered number
        """
        self.assertRegexpMatches(send_sms_with(REGISTER_DATA_SENDER), fetch_(SUCCESS_MESSAGE, from_(REGISTER_DATA_SENDER)))

    @attr('functional_test')
    def test_sms_player_for_addition_of_data_sender_from_unknown_number(self):
        self.assertEqual(send_sms_with(REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER),
                         fetch_(ERROR_MSG, from_(REGISTER_DATA_SENDER_FROM_UNKNOWN_NUMBER)))

    @attr('functional_test')
    def test_sms_player_for_registration_of_new_subject(self):
        organization = Organization.objects.get(org_id=DEFAULT_TEST_ORG_ID)
        message_tracker_before = organization._get_message_tracker(datetime.today())
        response = send_sms_with(REGISTER_NEW_SUBJECT)
        self.assertTrue(
            fetch_(SUCCESS_MESSAGE, from_(REGISTER_NEW_SUBJECT)) in response)
        message_tracker_after = organization._get_message_tracker(datetime.today())
        self.assertEqual(message_tracker_before.incoming_sms_count + 1, message_tracker_after.incoming_sms_count)
        self.assertEqual(message_tracker_before.sms_registration_count + 1, message_tracker_after.sms_registration_count)

    @attr('functional_test')
    def test_sms_player_for_registration_of_existing_subject_short_code(self):
        self.assertEqual(send_sms_with(REGISTER_EXISTING_SUBJECT_SHORT_CODE),
                         fetch_(ERROR_MSG, from_(REGISTER_EXISTING_SUBJECT_SHORT_CODE)))

    @attr('functional_test')
    def test_sms_player_for_registration_with_invalid_geo_code(self):
        self.assertEqual(send_sms_with(REGISTER_INVALID_GEO_CODE),
                         fetch_(ERROR_MSG, from_(REGISTER_INVALID_GEO_CODE)))

    @attr('functional_test')
    def test_sms_player_for_only_questionnaire_code(self):
        self.assertEqual(send_sms_with(ONLY_QUESTIONNAIRE_CODE), fetch_(ERROR_MSG, from_(ONLY_QUESTIONNAIRE_CODE)))

    @attr('functional_test')
    def test_sms_player_for_wrong_number_of_arg(self):
        self.assertEqual(send_sms_with(WRONG_NUMBER_OF_ARGS), fetch_(ERROR_MSG, from_(WRONG_NUMBER_OF_ARGS)))

    @attr('functional_test')
    def test_sms_player_for_unregistered_subject_and_invalid_geo_code(self):
        self.assertEqual(send_sms_with(UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA),
                         fetch_(ERROR_MSG, from_(UNREGISTER_ENTITY_ID_AND_SOME_INVALID_DATA)))
