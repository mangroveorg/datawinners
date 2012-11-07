# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
import mock
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import Mock, patch
from datawinners.messageprovider.messages import get_submission_success_message, get_registration_success_message
from mangrove.errors.MangroveException import FormModelDoesNotExistsException, NumberNotRegisteredException,\
    MangroveException, EntityQuestionCodeNotSubmitted
from datawinners.messageprovider.message_handler import get_exception_message_for, get_submission_error_message_for, get_success_msg_for_submission_using, get_success_msg_for_registration_using
from mangrove.transport.facade import  create_response_from_form_submission
import messageprovider
from messageprovider.message_builder import ResponseBuilder

THANKS = "Thank you. We received your message."


class TestGetExceptionMessageHandler(unittest.TestCase):
    def test_should_return_message_for_exception_for_channel(self):
        message = get_exception_message_for(exception=FormModelDoesNotExistsException("QC1"), channel="sms")
        expected_message = "Error with Questionnaire code QC1. Find the Questionnaire code on the printed questionnaire and resend SMS starting with this questionnaire code."
        self.assertEqual(expected_message, message)


    def test_should_return_default_message_for_exception_for_no_channel_passed(self):
        message = get_exception_message_for(exception=FormModelDoesNotExistsException("QC1"))
        expected_message = "Questionnaire ID QC1 doesnt exist."
        self.assertEqual(expected_message, message)


    def test_should_return_default_msg_for_exception_if_channel_specific_msg_missing(self):
        message = get_exception_message_for(exception=NumberNotRegisteredException("1234567890"), channel="web")
        expected_message = "This telephone number is not registered in our system."
        self.assertEqual(expected_message, message)


    def test_should_return_default_exception_message_for_unknown_exception(self):
        message = get_exception_message_for(exception=MangroveException(message="This is an error"), channel="web")
        expected_message = "This is an error"
        self.assertEqual(expected_message, message)

    def test_should_return_valid_message_even_if_code_is_None(self):
        message = get_exception_message_for(exception=EntityQuestionCodeNotSubmitted(), channel="web")
        expected_message = "This field is required."
        self.assertEqual(expected_message, message)

    def test_should_return_valid_message_if_its_not_parameterized(self):
        message = get_exception_message_for(exception=NumberNotRegisteredException("1234567"), channel="web")
        expected_message = "This telephone number is not registered in our system."
        self.assertEqual(expected_message, message)


class TestShouldTemplatizeMessage(unittest.TestCase):
    def test_should_format_error_message_with_question_codes(self):
        expected_message = u'Error. Incorrect answer for q1, q2. Please resend entire message.'
        errors = {"q1": "Some error", "q2": "Some other error"}
        message = get_submission_error_message_for(errors)
        self.assertEqual(expected_message, message)

    def create_form_submission_mock(self):
        form_submission_mock = Mock()
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.form_code = 'form_code'
        form_submission_mock.form_model = form_model_mock
        return form_submission_mock

    def test_should_format_success_message_for_submission_with_reporter_name(self):
        expected_message = THANKS + " age: 12 name: tester choice: red"
        form_submission_mock = self.create_form_submission_mock()
        response = create_response_from_form_submission(reporters=[{"name": "rep1"}], submission_id=123,
            form_submission=form_submission_mock)
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.stringify.return_value = {'name': 'tester', 'age': '12', 'choice': 'red'}
        message = get_success_msg_for_submission_using(response, form_model_mock)
        self.assertEqual(expected_message, message)

    def test_should_format_success_message_with_thanks_only_if_greater_than_160_characters(self):
        expected_message = THANKS
        response_text = "1"*125
        self.assertEqual(161, len(expected_message + response_text))
        with patch.object(ResponseBuilder, "get_expanded_response") as get_expanded_response:
            get_expanded_response.return_value = response_text
            message = get_success_msg_for_submission_using(Mock(), None)

        self.assertEqual(expected_message, message)

    def test_should_format_success_message_with_thanks_and_response_text_if_total_length_of_success_message_is_no_more_than_160_characters(self):
        response_text = "choice: rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        expected_message = THANKS + " " + response_text

        self.assertEqual(160, len(expected_message))

        with patch.object(ResponseBuilder, "get_expanded_response") as get_expanded_response:
            get_expanded_response.return_value = response_text
            message = get_success_msg_for_submission_using(Mock(), None)

        self.assertEqual(expected_message, message)
        self.assertTrue(160, len(message))

    def test_should_format_success_message_for_submission_with_blank_if_no_reporter(self):
        expected_message = THANKS + " name: tester"
        form_submission_mock = self.create_form_submission_mock()
        response = create_response_from_form_submission(reporters=[], submission_id=123,
            form_submission=form_submission_mock)
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.stringify.return_value = {'name': 'tester'}
        message = get_success_msg_for_submission_using(response, form_model_mock)
        self.assertEqual(expected_message, message)


    def test_should_format_success_message_for_registration_with_short_code(self):
        expected_message = get_registration_success_message() % "ID is: REP1"
        form_submission_mock = Mock()
        form_submission_mock.cleaned_data = {'name': 'tester'}
        form_submission_mock.short_code = "REP1"
        response = create_response_from_form_submission(reporters=[], submission_id=123,
            form_submission=form_submission_mock)
        message = get_success_msg_for_registration_using(response, "web")
        self.assertEqual(expected_message, message)
