import unittest
from django.contrib.auth.models import User
from accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from messageprovider.messages import SMS
from submission.request_processor import SMSTransportInfoRequestProcessor
from tests.data import DEFAULT_TEST_USER
from tests.fake_request import FakeRequest
from utils import get_organization_settings_from_request

class TestSMSRequestProcessor(unittest.TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        user = User.objects.get(username=DEFAULT_TEST_USER)
        self.mangrove_request = dict()
        self.sms_message = "Hi"
        self.from_number = "1234"
        self.to_number = "456"
        self.http_request = FakeRequest(post=dict(from_msisdn=self.from_number,to_msisdn=self.to_number,message=self.sms_message), user=user)

    def test_should_put_transport_info_in_request_for_sms_submission(self):
        processor = SMSTransportInfoRequestProcessor()
        processor.process(self.http_request, self.mangrove_request)
        self.assertEqual(SMS,self.mangrove_request['transport_info'].transport)
        self.assertEqual(self.from_number,self.mangrove_request['transport_info'].source)
        self.assertEqual(self.to_number,self.mangrove_request['transport_info'].destination)
