import unittest
from django.contrib.auth.models import User
from submission.request_processor import WebSMSDBMRequestProcessor
from tests.data import DEFAULT_TEST_USER, DEFAULT_TEST_ORG_ID, DEFAULT_TEST_ORG_NAME
from tests.fake_request import FakeRequest
from utils import generate_document_store_name

class TestWebSMSDBMProcessor(unittest.TestCase):
    fixtures = ['initial_data.json']
    def test_should_put_dbm_in_request_for_web_sms_submission(self):
        user = User.objects.get(username=DEFAULT_TEST_USER)
        request = FakeRequest(post=dict(test_mode=True), user=user)
        processor = WebSMSDBMRequestProcessor()
        processor.process(request)
        self.assertEqual(generate_document_store_name(DEFAULT_TEST_ORG_NAME,DEFAULT_TEST_ORG_ID), request['dbm'].database_name)


