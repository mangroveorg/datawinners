from django.utils import unittest
from django.test import Client

class TestWebSmsView(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_should_give_error_if_not_logged_in(self):
        response = self.client.post('/test_sms_submission/')
        self.assertEqual(302,response.status_code)

    def test_should_render_if_logged_in(self):
        self.client.login(username='tester150411@gmail.com',password='tester150411')
        response = self.client.post('/test_sms_submission/',{'message': '018 cli9 1.1.1002','test_mode': True, 'message_id':'test'})
        self.assertEqual(200,response.status_code)
