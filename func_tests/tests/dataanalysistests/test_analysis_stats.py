import json
import unittest

from nose.plugins.attrib import attr
from django.test import Client


@attr('functional_test')
class TestAnalysisStats(unittest.TestCase):
    def test_get_stats(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        data = {"search_filters": "{\"search_text\":\"Shweta\"}"}
        res = self.client.post("/project/submissions/cli018/analysis", data)
        expected = [{"count": 3, "term": "B+"}, {"count": 2, "term": "O+"}, {"count": 1, "term": "O-"},
                    {"count": 1, "term": "AB"}]
        response = json.loads(res.content)
        self.assertEquals(response['result'].get('What is your blood group?').get('data'), expected)
        self.assertEquals(response['result'].get('What is your blood group?').get('field_type'), 'select1')



