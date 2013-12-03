import json
from django.test import TestCase, Client


class TestAllDataSenderAutoCompleteView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_query_data_sender(self):
        response = self.client.get('/entity/datasenders/autocomplete/')
        response = json.loads(response.content)
        self.assertGreaterEqual(len(response), 0)
        print response
