from unittest import TestCase
from django.http import HttpRequest
from mock import Mock, patch
from datawinners.submission.views import sms, Responder


class TestSmsSubmission(TestCase):

    def test_should_trim_response_to_max_of_160_characters(self):
        with patch.object(Responder, 'respond') as respond:
            respond.return_value = "a"*161
            response = sms(Mock(spec=HttpRequest, method='POST'))
            self.assertEqual(response.content, "a"*160)
            self.assertEqual(160, len(response.content))

