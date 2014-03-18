import json
import unittest

from django.test import Client
from nose.plugins.attrib import attr


@attr('functional_test')
class TestAllSubjectsAutoCompleteView(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')


    def test_query_data_sender(self):
        response = self.client.get('/entity/clinic/autocomplete/?term=a')
        response = json.loads(response.content)
        self.assertGreaterEqual(len(response), 0)
        print response
