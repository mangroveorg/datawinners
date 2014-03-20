from django.test import Client, TestCase


class TestWebSmsView(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()

    def test_should_give_error_if_not_logged_in(self):
        response = self.client.post('/test_sms_submission/')
        self.assertEqual(302,response.status_code)
