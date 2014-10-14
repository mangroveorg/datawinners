import unittest
from mock import MagicMock, patch
from datawinners.project.send_message import get_data_sender_phone_numbers


class TestSendMessage(unittest.TestCase):

    def test_should_get_all_data_senders_numbers_when_all_data_senders_selected(self):
        dbm = MagicMock()
        form = MagicMock()
        form.cleaned_data = {'to': 'All'}
        with patch('datawinners.project.send_message.load_all_entities_of_type') as load_all_entities_mock:
            load_all_entities_mock.return_value = [{'cols': ['100']}, {'cols': ['200']}], ['mobile_number'], None

            all_data_sender_numbers = get_data_sender_phone_numbers(dbm, None, form)

            self.assertEqual(all_data_sender_numbers, ['100', '200'])

    def test_should_get_all_registered_data_senders_numbers_when_associated_data_senders_selected(self):
        dbm = MagicMock()
        project = MagicMock()
        form = MagicMock()

        form.cleaned_data = {'to': 'Associated'}
        project.get_data_senders.return_value = [{'mobile_number':'100'}, {'mobile_number':'200'}]

        all_data_sender_numbers = get_data_sender_phone_numbers(dbm, project, form)

        self.assertEqual(all_data_sender_numbers, ['100', '200'])

    def test_should_get_registered_and_unregistered_data_senders_associated_to_questionnaire_when_all_submitted_data_senders_selected(self):
        dbm = MagicMock()
        project = MagicMock()
        form = MagicMock()

        form.cleaned_data = {'to': 'AllSubmitted'}
        project.get_data_senders.return_value = [{'mobile_number':'100'}, {'mobile_number':'200'}]
        with patch('datawinners.project.send_message.get_unregistered_datasenders')as get_unregistered_datasenders:
            get_unregistered_datasenders.return_value = ['900', '800']

            actual_data_senders = get_data_sender_phone_numbers(dbm, project, form)

            self.assertEqual(actual_data_senders, ['100', '200', '900', '800'])

    def test_should_get_an_empty_array_when_other_numbers_selected(self):
        form = MagicMock()
        form.cleaned_data = {'to': 'others'}

        all_data_sender_numbers = get_data_sender_phone_numbers(None, None, form)

        self.assertEqual(all_data_sender_numbers, [])


