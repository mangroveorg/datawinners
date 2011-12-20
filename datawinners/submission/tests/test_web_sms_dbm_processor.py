import unittest
from django.contrib.auth.models import User
from accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from messageprovider.messages import SMS
from submission.request_processor import WebSMSDBMRequestProcessor, WebSMSTransportInfoRequestProcessor
from tests.data import DEFAULT_TEST_USER, DEFAULT_TEST_ORG_ID, DEFAULT_TEST_ORG_NAME
from tests.fake_request import FakeRequest
from utils import generate_document_store_name, get_organization_settings_from_request


class TestWebSMSRequestProcessor(unittest.TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        user = User.objects.get(username=DEFAULT_TEST_USER)
        self.request = FakeRequest(post=dict(test_mode=True), user=user)

    def test_should_put_dbm_in_request_for_web_sms_submission(self):
        processor = WebSMSDBMRequestProcessor()
        mangrove_request = dict()
        processor.process(self.request, mangrove_request)
        self.assertEqual(generate_document_store_name(DEFAULT_TEST_ORG_NAME,DEFAULT_TEST_ORG_ID), mangrove_request['dbm'].database_name)

    def test_should_put_transport_info_in_request_for_web_sms_submission(self):
        processor = WebSMSTransportInfoRequestProcessor()
        mangrove_request = dict()
        processor.process(self.request, mangrove_request)
        self.assertEqual(SMS,mangrove_request['transport_info'].transport)
        self.assertEqual(TEST_REPORTER_MOBILE_NUMBER,mangrove_request['transport_info'].source)
        organization_telephone_number = get_organization_settings_from_request(self.request).get_organisation_sms_number()
        self.assertEqual(organization_telephone_number,mangrove_request['transport_info'].destination)
