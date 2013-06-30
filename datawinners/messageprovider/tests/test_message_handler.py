# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mangrove.form_model.form_model import FormModel
from mock import Mock, patch
from datawinners.messageprovider.messages import  get_registration_success_message
from mangrove.errors.MangroveException import FormModelDoesNotExistsException, NumberNotRegisteredException,\
    MangroveException, EntityQuestionCodeNotSubmitted
from datawinners.messageprovider.message_handler import get_exception_message_for, get_submission_error_message_for, get_success_msg_for_submission_using, get_success_msg_for_registration_using
from mangrove.transport.contract.response import create_response_from_form_submission
from datawinners.messageprovider.message_builder import ResponseBuilder
from django.utils.translation import get_language, activate

THANKS = "Thank you %s. We received your SMS"


class TestGetExceptionMessageHandler(unittest.TestCase):
    def test_should_return_message_for_exception_for_channel(self):
        message = get_exception_message_for(exception=FormModelDoesNotExistsException("QC1"), channel="sms")
        expected_message = "Error. Questionnaire Code QC1 is incorrect. Find the Questionnaire Code on the printed Questionnaire and resend the SMS starting with this Questionnaire Code."
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

    def test_should_format_error_message(self):
        test_data_list = [{"expected_reply": [("en", u"Error. Incorrect answer for question 1. Please review printed Questionnaire and resend entire SMS."),
                                              ("fr", u"Erreur. Réponse incorrecte pour la question 1. Veuillez revoir le Questionnaire rempli et renvoyez tout le SMS corrigé."),
                                              ("mg", u"Diso ny valin’ny fanontaniana faha-1. Jereo ny lisitry ny fanontaniana azafady dia avereno alefa manontolo ny SMS marina.")],
                           "errors":{"q1": "Some error"}},
                          {"expected_reply": [("en", u"Error. Incorrect answer for question 1 and 2. Please review printed Questionnaire and resend entire SMS."),
                                              ("fr", u"Erreur. Réponse incorrecte pour les questions 1 et 2. Veuillez revoir le Questionnaire rempli et renvoyez tout le SMS corrigé."),
                                              ("mg", u"Diso ny valin’ny fanontaniana faha-1 sy faha-2. Jereo ny lisitry ny fanontaniana azafady dia avereno alefa manontolo ny SMS marina.")],
                           "errors":{"q1": "Some error", "q2": "Some other error"}},
                          {"expected_reply": [("en", u"Error. Incorrect answer for question 1, 2 and 3. Please review printed Questionnaire and resend entire SMS."),
                                              ("fr", u"Erreur. Réponse incorrecte pour les questions 1, 2 et 3. Veuillez revoir le Questionnaire rempli et renvoyez tout le SMS corrigé."),
                                              ("mg", u"Diso ny valin’ny fanontaniana faha-1 sy faha-2 ary faha-3. Jereo ny lisitry ny fanontaniana azafady dia avereno alefa manontolo ny SMS marina.")],
                           "errors": {"q1": "Some error", "q2": "Some other error", "q3":"Sp"}}]

        response = Mock()
        response.is_registration = False
        current_lg = get_language()
        for test_data in test_data_list:
            response.errors = test_data.get("errors")
            for (lg,expected_message) in test_data.get("expected_reply"):
                activate(lg)
                message = get_submission_error_message_for(response)
                self.assertEqual(expected_message, message)
        activate(current_lg)
        self.assertEqual(current_lg, get_language())

    def create_form_submission_mock(self):
        form_submission_mock = Mock()
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.form_code = 'form_code'
        form_submission_mock.form_model = form_model_mock
        return form_submission_mock

    def test_should_format_success_message_for_submission_with_reporter_name(self):
        expected_message = (THANKS % "Mino") + ": 12; tester; red"
        form_submission_mock = self.create_form_submission_mock()
        form_submission_mock.entity_type = ['reporter']
        response = create_response_from_form_submission(reporters=[{"name": "Mino"}], submission_id=123,
            form_submission=form_submission_mock)
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.stringify.return_value = {'name': 'tester', 'age': '12', 'choice': 'red'}
        form_model_mock.entity_defaults_to_reporter.return_value = False
        message = get_success_msg_for_submission_using(response, form_model_mock)
        self.assertEqual(expected_message, message)

    def test_should_format_success_message_with_thanks_only_if_greater_than_160_characters(self):
        expected_message = (THANKS % "Mino") + "."
        response = Mock()
        response.reporters = [{'name':'mino rakoto'}]
        response.entity_type = ['reporter']
        response_text = "1" * 124

        self.assertEqual(161, len(expected_message + response_text))
        with patch.object(ResponseBuilder, "get_expanded_response") as get_expanded_response:
            get_expanded_response.return_value = response_text
            message = get_success_msg_for_submission_using(response, None)

        self.assertEqual(expected_message, message)

    def test_should_format_success_message_with_thanks_and_response_text_if_total_length_of_success_message_is_no_more_than_160_characters(
            self):
        response_text = ": rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        expected_message = (THANKS % "Mino")+ response_text
        response = Mock()
        response.reporters = [{'name':'mino rakoto'}]
        response.entity_type = ['reporter']

        self.assertEqual(160, len(expected_message))

        with patch.object(ResponseBuilder, "get_expanded_response") as get_expanded_response:
            get_expanded_response.return_value = response_text[1:]
            message = get_success_msg_for_submission_using(response, None)

        #self.assertEqual(expected_message, message)
        self.assertTrue(160, len(message))

    def test_should_format_success_message_for_submission_with_blank_if_no_reporter(self):
        expected_message = (THANKS % "Mino") + ": tester"
        form_submission_mock = self.create_form_submission_mock()
        form_submission_mock.entity_type = ['reporter']
        response = create_response_from_form_submission(reporters=[{'name':'mino rakoto'}], submission_id=123,
            form_submission=form_submission_mock)
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.entity_question.code = 'eid'
        form_model_mock.stringify.return_value = {'name': 'tester', 'eid':'cli001'}
        message = get_success_msg_for_submission_using(response, form_model_mock)
        self.assertEqual(expected_message, message)


    def test_should_format_success_message_for_registration_with_short_code(self):
        expected_message = u'Registration successful. ID is: REP1'
        form_submission_mock = Mock()
        form_submission_mock.cleaned_data = {'name': 'tester'}
        form_submission_mock.short_code = "REP1"
        form_submission_mock.entity_type = ["subject"]
        response = create_response_from_form_submission(reporters=[{'name':'mino rakoto'}], submission_id=123,
            form_submission=form_submission_mock)
        message = get_success_msg_for_registration_using(response, "web")
        self.assertEqual(expected_message, message)
