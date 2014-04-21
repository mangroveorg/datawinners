import json
import unittest
from django.test import Client
from nose.plugins.attrib import attr
from framework.utils.common_utils import random_string
from testdata.constants import SENDER, RECEIVER, SMS
from tests.submissionlogtests.submission_log_tests import send_valid_sms_with
from tests.testdatasetup.project import create_project_with_multiple_unique_id_of_same_type


@attr('functional_test')
class TestSubmissionLogFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login(username='tester150411@gmail.com', password='tester150411')


    def test_filter_submissions_with_unique_id_filters(self):
        form_code = random_string(4)
        create_project_with_multiple_unique_id_of_same_type(self.client, form_code)
        answers = ["cid001 cid002 wp01", "cid003 cid004 wp03", "cid004 cid005 wp02"]
        for answer in answers:
            send_valid_sms_with({SENDER: '1234123413', RECEIVER: '919880734937', SMS: "%s %s" % (form_code, answer)})

        request = {"search_filters": '{"submissionDatePicker":"All Dates", "search_text":"", "uniqueIdFilters":{"clinic":"cid001", "waterpoint":""}}',
            'iDisplayStart':0,'iDisplayLength':25,'iSortCol_0':2
        }
        res = self.client.post("/project/submissions/%s?type=analysis" % form_code, request)
        self.assertEqual(1, len(json.loads(res.content).get('data')), res.content)

        request = {"search_filters": '{"submissionDatePicker":"All Dates", "search_text":"", "uniqueIdFilters":{"clinic":"cid004", "waterpoint":""}}',
            'iDisplayStart':0,'iDisplayLength':25,'iSortCol_0':2
        }
        res = self.client.post("/project/submissions/%s?type=analysis" % form_code, request)
        self.assertEqual(2, len(json.loads(res.content).get('data')), res.content)


