# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mangrove.errors.MangroveException import FormModelDoesNotExistsException, QuestionCodeAlreadyExistsException, NumberNotRegisteredException, MangroveException, EntityQuestionCodeNotSubmitted
from message_provider.message_handler import get_exception_message_for
from message_provider.messages import DEFAULT_EXCEPTION_MESSAGE

class TestExceptionHandler(unittest.TestCase):

    def test_should_return_message_for_exception_for_channel(self):
        message = get_exception_message_for(type=FormModelDoesNotExistsException, channel="sms", code="QC1")
        expected_message = "Error with Questionnaire ID QC1. Find the Questionnaire ID on the printed questionnaire and resend SMS"
        self.assertEqual(expected_message, message)


    def test_should_return_default_message_for_exception_for_no_channel_passed(self):
        message = get_exception_message_for(type=FormModelDoesNotExistsException, code="QC1")
        expected_message = "Questionnaire ID QC1 doesnt exist."
        self.assertEqual(expected_message, message)


    def test_should_return_default_msg_for_exception_if_channel_specific_msg_missing(self):
        message = get_exception_message_for(type=NumberNotRegisteredException, channel="web", code="QC1")
        expected_message = "This telephone number is not registered in our system."
        self.assertEqual(expected_message, message)


    def test_should_return_default_exception_message_for_unknown_exception(self):
        message = get_exception_message_for(type=MangroveException, channel="web", code="QC1")
        expected_message = DEFAULT_EXCEPTION_MESSAGE
        self.assertEqual(expected_message, message)

    def test_should_return_valid_message_even_if_code_is_None(self):
        message = get_exception_message_for(type=EntityQuestionCodeNotSubmitted, channel="web")
        expected_message = "You have not created a question asking the collector for the subject he is reporting on"
        self.assertEqual(expected_message, message)

    def test_should_return_valid_message_if_its_not_parameterized(self):
        message = get_exception_message_for(type=NumberNotRegisteredException, channel="web", code="QC1")
        expected_message = "This telephone number is not registered in our system."
        self.assertEqual(expected_message, message)


