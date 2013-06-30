# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock, patch
from datawinners.submission.models import SMSResponse
from mangrove.form_model.form_model import NAME_FIELD, FormModel
from mangrove.transport.contract.response import Response
from datawinners.messageprovider.tests.test_message_handler import THANKS

class TestSMSResponse(unittest.TestCase):

    def setUp(self):
        self.form_submission_mock = Mock()
        self.form_submission_mock.cleaned_data = {'name': 'Clinic X'}
        self.form_submission_mock.saved.return_value = True
        self.form_submission_mock.short_code = "CLI001"

    def test_should_return_expected_success_response(self):
        self.form_submission_mock.is_registration = False
        response = Response([{NAME_FIELD: "Mino X"}], None, None, self.form_submission_mock.saved, self.form_submission_mock.errors,
            self.form_submission_mock.data_record_id,
            self.form_submission_mock.short_code, self.form_submission_mock.cleaned_data, self.form_submission_mock.is_registration,
            ['reporter'],
            self.form_submission_mock.form_model.form_code)

        dbm_mock = Mock()
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.stringify.return_value = {'name': 'Clinic X','eid':'cli001'}
        form_model_mock.entity_question.code = 'eid'
        with patch("datawinners.messageprovider.message_handler.get_form_model_by_code") as get_form_model_mock:
            get_form_model_mock.return_value = form_model_mock
            response_text = SMSResponse(response).text(dbm_mock)
        self.assertEqual((THANKS % "Mino") + u": Clinic X", response_text)

    def test_should_return_expected_success_response_for_registration(self):
        self.form_submission_mock.is_registration = True

        response = Response([{NAME_FIELD: "Mr. X"}], None, None, self.form_submission_mock.saved,
            self.form_submission_mock.errors,
            self.form_submission_mock.data_record_id,
            self.form_submission_mock.short_code, self.form_submission_mock.cleaned_data,
            self.form_submission_mock.is_registration,
            ['clinic'],
            self.form_submission_mock.form_model.form_code)

        dbm_mock = Mock()
        form_model_mock = Mock(spec=FormModel)
        form_model_mock.stringify.return_value = {'name': 'Clinic X', 'eid':'cli001'}
        form_model_mock.entity_question.code = 'eid'
        with patch("datawinners.messageprovider.message_handler.get_form_model_by_code") as get_form_model_mock:
            get_form_model_mock.return_value = form_model_mock
            response_text = SMSResponse(response).text(dbm_mock)
        self.assertEqual("Thank you Mr., We registered your clinic: Clinic X", response_text)

    def test_should_return_expected_error_response(self):
        self.form_submission_mock.saved = False
        error_response = "horrible hack. feeling bad about it. But need to change mangrove error handling and error response"
        self.form_submission_mock.errors = error_response

        response = Response([], None, None, self.form_submission_mock.saved,
            self.form_submission_mock.errors,
            self.form_submission_mock.data_record_id,
            self.form_submission_mock.short_code, self.form_submission_mock.cleaned_data,
            self.form_submission_mock.is_registration,
            self.form_submission_mock.entity_type,
            self.form_submission_mock.form_model.form_code)

        self.assertEqual(error_response, SMSResponse(response).text(Mock(spec=FormModel)))
