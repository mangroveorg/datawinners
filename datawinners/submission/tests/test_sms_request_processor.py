import unittest
from django.contrib.auth.models import User
from django.test import TestCase
from datawinners.messageprovider.messages import SMS
from datawinners.submission.request_processor import SMSTransportInfoRequestProcessor
from datawinners.tests.data import DEFAULT_TEST_USER, DEFAULT_TEST_ORG_TEL_NO
from datawinners.tests.fake_request import FakeRequest

class TestSMSRequestProcessor(TestCase):


    fixtures = ['test_data.json']

    def setUp(self):
        user = User.objects.get(username=DEFAULT_TEST_USER)
        self.mangrove_request = dict()
        self.sms_message = "Hi"
        self.from_number = "1234"
        self.to_number = DEFAULT_TEST_ORG_TEL_NO
        self.http_request = FakeRequest(post=dict(from_msisdn=self.from_number,to_msisdn=self.to_number,message=self.sms_message), user=user)

    def test_should_put_transport_info_in_request_for_sms_submission(self):
        processor = SMSTransportInfoRequestProcessor()
        processor.process(self.http_request, self.mangrove_request)
        self.assertEqual(SMS,self.mangrove_request['transport_info'].transport)
        self.assertEqual(self.from_number,self.mangrove_request['transport_info'].source)
        self.assertEqual(self.to_number,self.mangrove_request['transport_info'].destination)

