from django.test import TestCase
from django.test import Client

class TestDataExtraction(TestCase):
    def setUp(self):
        self.client = Client()

    def test_should_get_data_by_subject(self):
        response = self.client.get('/api/get_by_subject/clinic/cid001/')
        self.assertEquals(response.status_code, 200)