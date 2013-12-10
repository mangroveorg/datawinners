import json
from django.test import TestCase, Client


class TestAllDataSenderAutoCompleteView(TestCase):
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
