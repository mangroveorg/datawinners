from django.utils import unittest
from django.test import Client
from django.utils.unittest.case import SkipTest


@SkipTest #functional_test
class TestSmsView(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_should_render_if_logged_in(self):
        response = self.client.post('/submission',{'to_msisdn': u'919880734937', 'message': u'cli001 cid001 abc 45 10.10.2011 a a 1,1 a', 'from_msisdn': u'1234567890', 'message_id':"234"})
        self.assertEqual(200,response.status_code)
