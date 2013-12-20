import json
from django.test import TestCase, Client
from django.utils import unittest

class TestAnalysisStats(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def test_get_stats(self):
        data = {"search_filters":"{\"search_text\":\"Shweta\"}"}
        res = self.client.post("/project/submissions/cli018/analysis", data)
        expected = [{"count": 3, "term": "b+"}, {"count": 2, "term": "o+"}, {"count": 1, "term": "o-"}, {"count": 1, "term": "ab"}]
        result = json.loads(res.content)
        self.assertEquals(expected, result.values()[0])
