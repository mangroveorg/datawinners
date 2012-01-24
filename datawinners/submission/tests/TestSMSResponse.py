# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mock import Mock
from datawinners.submission.models import SMSResponse
from mangrove.form_model.form_model import NAME_FIELD
from mangrove.transport.player.player import Response

class TestSMSResponse(unittest.TestCase):
    def setUp(self):
        self.form_submission_mock = Mock()
        self.form_submission_mock.cleaned_data = {'name': 'Clinic X'}
        self.form_submission_mock.saved.return_value = True
        self.form_submission_mock.short_code = "CLI001"

    def test_should_return_expected_success_response(self):
        self.form_submission_mock.is_registration = False
        response = Response(reporters=[{ NAME_FIELD : "Mr. X"}], submission_id=123,form_submission=self.form_submission_mock)
        self.assertEqual(u"Thank you Mr. X. We received : name: Clinic X", SMSResponse(response).text())

    def test_should_return_expected_success_response_for_registration(self):
        self.form_submission_mock.is_registration = True

        response = Response(reporters=[{ NAME_FIELD : "Mr. X"}], submission_id=123,form_submission=self.form_submission_mock)
        self.assertEqual(u'Registration successful. Unique identification number(ID) is: CLI001.We received : name: Clinic X',
                         SMSResponse(response).text())

    def test_should_return_expected_error_response(self):
        self.form_submission_mock.saved= False
        error_response = "horrible hack. feeling bad about it. But need to change mangrove error handling and error response"
        self.form_submission_mock.errors= error_response


        response = Response(reporters=[], submission_id=123,form_submission=self.form_submission_mock)
        self.assertEqual(error_response,
                         SMSResponse(response).text())
