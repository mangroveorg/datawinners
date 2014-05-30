# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import OrderedDict
import unittest

from mock import Mock, patch, MagicMock
from django.utils.translation import get_language, activate
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from mangrove.errors.MangroveException import FormModelDoesNotExistsException, NumberNotRegisteredException, \
    MangroveException, EntityQuestionCodeNotSubmitted, SMSParserWrongNumberOfAnswersException
from mangrove.transport.contract.response import create_response_from_form_submission

from datawinners.messageprovider.message_handler import get_exception_message_for, get_submission_error_message_for, \
    get_success_msg_for_ds_registration_using, _is_unique_id_not_present_error


THANKS = "Thank you %s. We received your SMS"


class TestGetExceptionMessageHandler(unittest.TestCase):
    def test_should_return_message_for_exception_for_channel(self):
        message = get_exception_message_for(exception=FormModelDoesNotExistsException("QC1"), channel="sms")
        expected_message = "Error. Questionnaire Code QC1 is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code."
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

    def test_should_return_exception_message_for_incorrect_number_of_sms_answers(self):
        message = get_exception_message_for(exception=SMSParserWrongNumberOfAnswersException("form_code"), channel="sms")
        expected_message = u'Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.'
        self.assertEqual(expected_message, message)


class TestShouldTemplatizeMessage(unittest.TestCase):


    # def test_should_format_error_message(self):
    #     test_data_list = [{"expected_reply": [("en", u"Error. Incorrect answer for question 1. Please review printed Questionnaire and resend entire SMS."),
    #                                           ("fr", u"Erreur. Reponse incorrecte pour la question 1. Veuillez revoir le Questionnaire imprime et renvoyez le SMS en entier."),
    #                                           ("mg", u"Diso. Valiny diso hoan'ny fanontaniana faha-1. Amarino ny vondrom-panontaniana ary avereno alefa ny SMS iray manontolo."),
    #                                           ("pt", u"Erro. Resposta incorrecta para a pergunta 1. Por favor reveja o questionario impresso e reenvie a SMS inteira.")],
    #                        "errors":{"N": "Some error"}},
    #                       {"expected_reply": [("en", u"Error. Incorrect answer for question 1 and 2. Please review printed Questionnaire and resend entire SMS."),
    #                                           ("fr", u"Erreur. Reponse incorrecte pour les questions 1 et 2. Veuillez revoir le Questionnaire imprime et renvoyez le SMS en entier."),
    #                                           ("mg", u"Diso. Valiny diso hoan'ny fanontaniana faha-1 sy faha-2. Amarino ny vondrom-panontaniana ary avereno alefa ny SMS iray manontolo."),
    #                                           ("pt", u"Erro. Resposta incorrecta para a pergunta 1 e 2. Por favor reveja o questionario impresso e reenvie a SMS inteira.")],
    #                        "errors":{"FA": "Some error", "n": "Some other error"}},
    #                       {"expected_reply": [("en", u"Error. Incorrect answer for question 1, 2 and 3. Please review printed Questionnaire and resend entire SMS."),
    #                                           ("fr", u"Erreur. Reponse incorrecte pour les questions 1, 2 et 3. Veuillez revoir le Questionnaire imprime et renvoyez le SMS en entier."),
    #                                           ("mg", u"Diso. Valiny diso hoan'ny fanontaniana faha-1 sy faha-2 ary faha-3. Amarino ny vondrom-panontaniana ary avereno alefa ny SMS iray manontolo."),
    #                                           ("pt", u"Erro. Resposta incorrecta para a pergunta 1, 2 e 3. Por favor reveja o questionario impresso e reenvie a SMS inteira.")],
    #                        "errors": {"Fa": "Some error", "n": "Some other error", "pl":"Sp"}}]
    #
    #     response = Mock()
    #     response.is_registration = False
    #     current_lg = get_language()
    #     form_model_mock = Mock(spec=FormModel,_dbm=Mock(), fields=[TextField("name", "n","Father's name"), TextField("age", "fa","Father's age"),TextField("place", "pl","Father's Place")])
    #     with patch(
    #             "datawinners.messageprovider.customized_message.get_form_model_by_code") as get_form_model_by_code_mock:
    #         with patch("datawinners.messageprovider.customized_message.Project") as project_mock:
    #             project_mock.from_form_model = Mock(return_value=Mock(language="en"))
    #             get_form_model_by_code_mock.return_value=form_model_mock
    #             for test_data in test_data_list:
    #                 response.errors = test_data.get("errors")
    #                 for (lg,expected_message) in test_data.get("expected_reply"):
    #                     activate(lg)
    #                     message = get_submission_error_message_for(response, form_model=form_model_mock, dbm=MagicMock(spec= DatabaseManager, database=Mock(name="a")), request=None)
    #                     self.assertEqual(expected_message, message)
    #             activate(current_lg)
    #             self.assertEqual(current_lg, get_language())

    def create_form_submission_mock(self):
        form_submission_mock = Mock()
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.form_code = 'form_code'
        form_submission_mock.form_model = form_model_mock
        return form_submission_mock

    #def test_should_format_success_message_for_submission_with_reporter_name(self):
    #    expected_message = (THANKS % "Mino") + ": 12; tester; red"
    #    form_submission_mock = self.create_form_submission_mock()
    #    form_submission_mock.entity_type = ['reporter']
    #    response = create_response_from_form_submission(reporters=[{"name": "Mino"}],
    #                                                    form_submission=form_submission_mock)
    #    form_model_mock = Mock(spec=FormModel)
    #    form_model_mock.stringify.return_value = {'name': 'tester', 'age': '12', 'choice': 'red'}
    #    message = get_success_msg_for_submission_using(response, form_model_mock)
    #    self.assertEqual(expected_message, message)

    #def test_should_format_success_message_with_thanks_only_if_greater_than_160_characters(self):
    #    expected_message = (THANKS % "Mino") + "."
    #    response = Mock()
    #    response.reporters = [{'name': 'mino rakoto'}]
    #    response.entity_type = ['reporter']
    #    response_text = "1" * 124
    #
    #    self.assertEqual(161, len(expected_message + response_text))
    #    with patch.object(ResponseBuilder, "get_expanded_response") as get_expanded_response:
    #        get_expanded_response.return_value = response_text
    #        message = get_success_msg_for_submission_using(response, None)
    #
    #    self.assertEqual(expected_message, message)

    #def test_should_format_success_message_with_thanks_and_response_text_if_total_length_of_success_message_is_no_more_than_160_characters(
    #        self):
    #    response_text = ": rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
    #    expected_message = (THANKS % "Mino") + response_text
    #    response = Mock()
    #    response.reporters = [{'name': 'mino rakoto'}]
    #    response.entity_type = ['reporter']
    #
    #    self.assertEqual(160, len(expected_message))
    #
    #    with patch.object(ResponseBuilder, "get_expanded_response") as get_expanded_response:
    #        get_expanded_response.return_value = response_text[1:]
    #        message = get_success_msg_for_submission_using(response, None)
    #
    #    #self.assertEqual(expected_message, message)
    #    self.assertTrue(160, len(message))


    def test_should_format_success_message_for_registration_with_short_code(self):
        expected_message = u'Registration successful. ID is: REP1'
        form_submission_mock = Mock()
        form_submission_mock.cleaned_data = {'name': 'tester'}
        form_submission_mock.short_code = "REP1"
        form_submission_mock.entity_type = ["subject"]
        response = create_response_from_form_submission(reporters=[{'name': 'mino rakoto'}],
                                                        form_submission=form_submission_mock)
        message = get_success_msg_for_ds_registration_using(response, "web")
        self.assertEqual(expected_message, message)

    def test_should_return_unique_id_field_errors_separately_when_multiple_answer_type_errors_present(self):
        errors = {"q1": "clinic with Unique Identification Number (ID) = cli001 not found",
                  "q2": "Expected date found number"}
        form_model = MagicMock()
        form_model.form_code = 'form_code'
        dbm = MagicMock(spec=DatabaseManager)
        request = {}
        response = MagicMock(errors=errors)

        with patch(
                "datawinners.messageprovider.handlers.get_customized_message_for_questionnaire") as get_customized_message_for_questionnaire_mock:
            get_submission_error_message_for(response, form_model, dbm, request)

            get_customized_message_for_questionnaire_mock.assert_called_with(dbm, None,
                                                                             'reply_identification_number_not_registered',
                                                                             'form_code', placeholder_dict={
                    'Submitted Identification Number': 'cli001'})

    def test_should_return_first_unique_id_field_errors_separately_when_multiple_answer_type_errors_present(self):
        # When there are multiple unique id questions in the questionnaire, error response should contain first
        # unique id error among unique ids.

        errors = OrderedDict([
            ("q1","answer exceeds number of characters."),
                             ("q2", "clinic with Unique Identification Number (ID) = cli001 not found"),
        ("q3", "school with Unique Identification Number (ID) = sch001 not found"),
        ("q4", "Expected date found number")])
        form_model = MagicMock()
        dbm = MagicMock(spec=DatabaseManager)
        form_model.form_code = 'form_code'
        response = MagicMock(errors=errors)
        request = {}

        with patch(
                "datawinners.messageprovider.handlers.get_customized_message_for_questionnaire") as get_customized_message_for_questionnaire_mock:

            get_submission_error_message_for(response, form_model, dbm, request)


            get_customized_message_for_questionnaire_mock.assert_called_with(dbm, None,
                                                                             'reply_identification_number_not_registered',
                                                                             'form_code', placeholder_dict={
                    'Submitted Identification Number': 'cli001'})

    def test_should_return_invalid_unique_id_code_and_unique_id_type_from_error_message(self):
        errors = {"q2": "my clinics with Unique Identification Number (ID) = cl.i0.01 not found"}
        is_errors_present, unique_id_type, invalid_code = _is_unique_id_not_present_error(errors)
        self.assertTrue(is_errors_present)
        self.assertEqual(unique_id_type, "my clinics")
        self.assertEqual(invalid_code, "cl.i0.01")
