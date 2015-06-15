import unittest

from django.test import Client
from nose.plugins.attrib import attr
from datawinners.utils import random_string

from tests.datasendertests.data_sender_activation_email_helper import create_questionnaire
from tests.logintests.login_data import VALID_CREDENTIALS, USERNAME, PASSWORD


class SendAMessageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login(username=VALID_CREDENTIALS[USERNAME], password=VALID_CREDENTIALS[PASSWORD])
        cls.admin_client = Client()
        cls.admin_client.login(username='datawinner', password='d@t@winner')
        cls.project_id = create_questionnaire(cls.client)

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_message_sent_to_registered_datasenders(self):
        random_message = random_string(10)
        response = self.client.post(
            path='/project/broadcast_message/'+self.project_id+'/',
            data={
                'others':'',
                'text':random_message,
                'to':'Associated'
            })
        self.assertIn('SMS sent to telephone company. Upon receipt of delivery confirmation, DataWinners will update the counter on the', response.content)

        response = self.admin_client.post(path='/admin-apis/sendamessage/check_if_message_present_in_postgres/',
                                    data={'message': random_message})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_message_sent_to_all_datasenders(self):
        random_message = random_string(10)
        response = self.client.post(
            path='/project/broadcast_message/'+self.project_id+'/',
            data={
                'others':'',
                'text':random_message,
                'to':'All'
            })
        self.assertIn('SMS sent to telephone company. Upon receipt of delivery confirmation, DataWinners will update the counter on the', response.content)

        response = self.admin_client.post(path='/admin-apis/sendamessage/check_if_message_present_in_postgres/',
                                    data={'message': random_message})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_message_sent_to_all_submitted_datasenders(self):
        random_message = random_string(10)
        response = self.client.post(
            path='/project/broadcast_message/'+self.project_id+'/',
            data={
                'others':'',
                'text':random_message,
                'to':'AllSubmitted'
            })
        self.assertIn('SMS sent to telephone company. Upon receipt of delivery confirmation, DataWinners will update the counter on the', response.content)

        response = self.admin_client.post(path='/admin-apis/sendamessage/check_if_message_present_in_postgres/',
                                    data={'message': random_message})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_message_sent_to_others(self):
        random_message = random_string(10)
        response = self.client.post(
            path='/project/broadcast_message/'+self.project_id+'/',
            data={
                'others':'141231241, 121242141',
                'text':random_message,
                'to':'Additional'
            })
        self.assertIn('SMS sent to telephone company. Upon receipt of delivery confirmation, DataWinners will update the counter on the', response.content)

        response = self.admin_client.post(path='/admin-apis/sendamessage/check_if_message_present_in_postgres/',
                                    data={'message': random_message})
        self.assertEqual(response.content, '{"found": true}')