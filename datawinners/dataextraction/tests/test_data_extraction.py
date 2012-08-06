from django.test import TestCase
from django.test import Client

class TestDataExtraction(TestCase):
    def setUp(self):
        self.client = Client()

    def test_should_get_data_by_subject(self):
        response = self.client.get('/api/get_for_subject/clinic/cid001/')
        self.assertEquals(response.status_code, 200)

    def test_should_return_with_forbidden_error_when_get_data_by_subject_with_post_method(self):
        response = self.client.post('/api/get_for_subject/clinic/cid001/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "Error. Only support GET method.")

    def test_should_get_data_by_subject_and_date(self):
        response = self.client.get('/api/get_for_subject/clinic/cid001/03-08-2012/06-08-2012/')
        self.assertEquals(response.status_code, 200)