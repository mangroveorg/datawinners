import unittest
from django.contrib.auth.models import User
from accountmanagement.models import Organization
from submission.request_processor import SMSMessageRequestProcessor, SMSTransportInfoRequestProcessor
from submission.views import submit_to_player
from tests.data import DEFAULT_TEST_ORG_ID, DEFAULT_TEST_USER, TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, DEFAULT_TEST_ORG_TEL_NO
from tests.fake_request import FakeRequest
import utils

class TestSubmitToPlayer(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.get(username=DEFAULT_TEST_USER)
        self.mangrove_request = dict()
        organization = Organization.objects.get(pk=DEFAULT_TEST_ORG_ID)
        self.mangrove_request['dbm'] = utils.get_database_manager_for_org(organization)

    def test_should_return_success_message(self):
        sms_message = "cli001 cid001 abc 45 10.10.2011 a a 1,1 a"
        http_request = FakeRequest(post=dict(from_msisdn=TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,to_msisdn=DEFAULT_TEST_ORG_TEL_NO,message=sms_message), user=self.user)
        SMSMessageRequestProcessor().process(http_request=http_request, mangrove_request=self.mangrove_request)
        SMSTransportInfoRequestProcessor().process(http_request=http_request, mangrove_request=self.mangrove_request)

        message = "Thank you Shweta. We received : EID: cid001 NA: abc FA: 45.0 RD: 10.10.2011 BG: O+ SY: Rapid weight loss GPS: 1.0,1.0 RM: Hivid"
        self.mangrove_request = submit_to_player(self.mangrove_request)
        self.assertEquals(message,self.mangrove_request['outgoing_message'])

    def test_should_return_error_message(self):
        sms_message = "cli001 cid001 abc 45 10.10.2011 a a 1,1 a 12"
        http_request = FakeRequest(post=dict(from_msisdn=TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,to_msisdn=DEFAULT_TEST_ORG_TEL_NO,message=sms_message), user=self.user)
        SMSMessageRequestProcessor().process(http_request=http_request, mangrove_request=self.mangrove_request)
        SMSTransportInfoRequestProcessor().process(http_request=http_request, mangrove_request=self.mangrove_request)

        message = "Error. Incorrect number of answers submitted. Review printed questionnaire and resend SMS."
        self.mangrove_request = submit_to_player(self.mangrove_request)
        self.assertEquals(message,self.mangrove_request['outgoing_message'])
