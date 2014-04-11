from django.test import TestCase, Client

class TestDataExtraction(TestCase):
    def setUp(self):
        self.client = Client()

    def test_should_authenticate_with_digest_authentication_to_get_data_for_form(self):
        response = self.client.get('/api/get_for_form/cli/')
        self.assertEquals(response.status_code, 401)

