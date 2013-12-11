import json
from django.test import TestCase, Client


class TestAutoCompleteView(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def test_query_data_sender_by_datasender_name(self):
        datasender_name = "Tester Pune"
        response = self.client.get('/entity/datasenders/autocomplete/?term=' + datasender_name)
        response = json.loads(response.content)
        self.assertEquals(response[0].get('label'), datasender_name)

    def test_query_data_sender_by_datasender_id(self):
        repid = "rep276"
        response = self.client.get('/entity/datasenders/autocomplete/?term=' + repid)
        response = json.loads(response.content)
        self.assertEquals(response[0].get('id'), repid)

    def test_query_subject_by_name(self):
        subject_name = "test"
        response = self.client.get('/entity/Clinic/autocomplete/?term=' + subject_name)
        response = json.loads(response.content)
        self.assertGreaterEqual(len(response), 0)
        print response

    def test_query_subject_by_id(self):
        subject_id = "cid001"
        response = self.client.get('/entity/Clinic/autocomplete/?term=' + subject_id)
        response = json.loads(response.content)
        self.assertGreaterEqual(len(response), 0)
        print response