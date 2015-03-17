from unittest import TestCase
from mock import MagicMock
from datawinners.entity.view.send_sms import SendSMS


class TestSMS(TestCase):

    def test_should_return_unique_mobile_numbers(self):
        mock_request = MagicMock()
        mock_request.POST = {"others": "87687687,9879879, 9879879"}

        actual_numbers = SendSMS()._other_numbers(mock_request)
        expected_numbers = list(set(["87687687", "9879879"]))
        self.assertListEqual(actual_numbers, expected_numbers)