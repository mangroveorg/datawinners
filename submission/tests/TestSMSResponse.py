# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datawinners.submission.models import SMSResponse
from mangrove.form_model.form_model import NAME_FIELD
from mangrove.transport.player.player import Response
from mangrove.transport.submissions import SubmissionResponse

class TestSMSResponse(unittest.TestCase):
    def test_should_return_expected_success_response(self):
        response = Response(reporters=[{ NAME_FIELD : "Mr. X"}], submission_response=SubmissionResponse(
            True, "1", datarecord_id="2", short_code="CLI001",
            processed_data={'name': 'Clinic X'}))
        self.assertEqual(u"Thank you Mr. X. We received : name: Clinic X", SMSResponse(response).text())

    def test_should_return_expected_success_response_for_registration(self):
        response = Response(reporters=[{ NAME_FIELD : "Mr. X"}], submission_response=SubmissionResponse(
            True, "1", datarecord_id="2", short_code="CLI001",
            processed_data={'name': 'Clinic X'},is_registration = True))
        self.assertEqual(u'Registration successful. Subject identification number: CLI001.We received : name: Clinic X',
                         SMSResponse(response).text())
