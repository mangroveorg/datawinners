import unittest
from django.contrib.auth.models import User
from django.test import TestCase
from mangrove.datastore.database import DatabaseManager
from mock import patch, Mock
from datawinners.settings import TRIAL_ACCOUNT_PHONE_NUMBER
from datawinners.submission.views import find_dbm
from datawinners.tests.data import TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, DEFAULT_TEST_ORG_TEL_NO, DEFAULT_TEST_USER
from datawinners.tests.fake_request import FakeRequest

class TestFindDBM(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.user = User.objects.get(username=DEFAULT_TEST_USER)
        self.sms_message = '018 12.10.2011'

    def test_should_go_to_next_state_if_post_data_is_correct(self):
         with patch('datawinners.main.database.mangrove_db_manager') as mangrove_db_manager:
            mangrove_db_manager.side_effect = lambda server, database, credentials: Mock(spec=DatabaseManager, database_name = database)
            request = FakeRequest(post=dict(from_msisdn=TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,to_msisdn=DEFAULT_TEST_ORG_TEL_NO,message=self.sms_message), user=self.user)
            incoming_request = find_dbm(request)
            self.assertTrue('outgoing_message' not in incoming_request.keys())

    def test_should_return_error_message_when_organization_number_is_unregistered(self):
        request = FakeRequest(post=dict(from_msisdn=TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO,to_msisdn='1234567',message=self.sms_message), user=self.user)
        incoming_request = find_dbm(request)
        self.assertTrue('outgoing_message' in incoming_request.keys())

    def test_should_return_error_message_when_datasenders_number_is_unregistered(self):
        request = FakeRequest(post=dict(from_msisdn='1234567',to_msisdn=TRIAL_ACCOUNT_PHONE_NUMBER[0],message=self.sms_message), user=self.user)
        incoming_request = find_dbm(request)
        self.assertTrue('outgoing_message' in incoming_request.keys())
