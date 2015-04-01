from unittest import TestCase
from mock import MagicMock, Mock, patch
from datawinners.entity.view.send_sms import SendSMS
from mangrove.datastore.database import DatabaseManager


class TestSMS(TestCase):

    def test_should_return_unique_mobile_numbers(self):
        mock_request = MagicMock()
        mock_request.POST = {"others": "87687687,9879879, 9879879", "recipient": "others"}

        actual_numbers = SendSMS()._other_numbers(mock_request)
        expected_numbers = list(set(["87687687", "9879879"]))
        self.assertListEqual(actual_numbers, expected_numbers)

    def test_should_fetch_mobile_numbers_for_given_questionnaire_names_when_recipient_is_linked(self):
        dbm = MagicMock(spec=DatabaseManager)
        request = MagicMock()
        request.POST = {'recipient': "linked", 'questionnaire-names': '["questionnaire1", "questionnaire2"]'}

        with patch("datawinners.entity.view.send_sms.SendSMS._mobile_numbers_for_questionnaire") as mock_mobile_numbers_for_questionnaire:
            mock_mobile_numbers_for_questionnaire.return_value = ["72465823", "4837539"]

            mobile_numbers = SendSMS()._get_mobile_numbers_for_registered_data_senders(dbm, request)

            mock_mobile_numbers_for_questionnaire.assert_called_once_with(dbm, ["questionnaire1", "questionnaire2"])

            self.assertListEqual(mobile_numbers, ["72465823", "4837539"])

    def test_should_fetch_no_mobile_numbers_when_recipient_is_others(self):
        dbm = MagicMock(spec=DatabaseManager)
        request = MagicMock()
        request.POST = {'recipient': "others"}

        mobile_numbers = SendSMS()._get_mobile_numbers_for_registered_data_senders(dbm, request)

        self.assertListEqual(mobile_numbers, [])
