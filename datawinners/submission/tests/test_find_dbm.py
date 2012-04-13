import unittest
from django.contrib.auth.models import User
from datawinners.settings import TRIAL_ACCOUNT_PHONE_NUMBER
from datawinners.submission.views import find_dbm
from datawinners.tests.data import DEFAULT_TEST_USER, TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, DEFAULT_TEST_ORG_TEL_NO
from datawinners.tests.fake_request import FakeRequest

class TestFindDBM(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.get(username=DEFAULT_TEST_USER)
        self.sms_message = '018 12.10.2011'

    def test_should_go_to_next_state_if_post_data_is_correct(self):
        request = FakeRequest(post=dict(from_addr=TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,to_addr=DEFAULT_TEST_ORG_TEL_NO,content=self.sms_message), user=self.user)
        incoming_request = find_dbm(request)
        self.assertTrue('outgoing_message' not in incoming_request.keys())

    def test_should_return_error_message_when_organization_number_is_unregistered(self):
        request = FakeRequest(post=dict(from_addr=TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,to_addr='1234567',content=self.sms_message), user=self.user)
        incoming_request = find_dbm(request)
        self.assertTrue('outgoing_message' in incoming_request.keys())

    def test_should_return_error_message_when_datasenders_number_is_unregistered(self):
        request = FakeRequest(post=dict(from_addr='1234567',to_addr=TRIAL_ACCOUNT_PHONE_NUMBER[0],content=self.sms_message), user=self.user)
        incoming_request = find_dbm(request)
        self.assertTrue('outgoing_message' in incoming_request.keys())
