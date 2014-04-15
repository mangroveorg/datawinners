import json
import unittest

from nose.plugins.attrib import attr
from django.test import Client
from framework.utils.common_utils import random_string
from testdata.constants import SENDER, RECEIVER, SMS
from tests.submissionlogtests.submission_log_tests import send_valid_sms_with
from tests.testdatasetup.project import create_multi_choice_project

form_code = random_string()
VALID_SMS_BLOOD_A = {SENDER: '1234123413', RECEIVER: '919880734937', SMS: "%s a" % form_code, }


@attr('functional_test')
class TestAnalysisStats(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login(username='tester150411@gmail.com', password='tester150411')
        create_multi_choice_project(cls.client, form_code)
        for answer in ["a 12.03.2014 01.2015", "b 10.05.2014 01.2015", "d 10.05.2015 03.2015", "a 10.03.2014 04.2015"]:
            send_valid_sms_with({SENDER: '1234123413', RECEIVER: '919880734937', SMS: "%s %s" % (form_code, answer)})

    def test_get_stats(self):
        data = {"search_filters": "{\"search_text\":\"\",\"dateQuestionFilters\":{}}"}

        res = self.client.post("/project/submissions/%s/analysis" % form_code, data)

        expected = set([(2, "A"), (1, "B"), (0, "AB"), (1, "O")])
        response = json.loads(res.content)
        actual_stat = set([(i["count"], i["term"]) for i in response['result'].get('Blood Group').get('data')])
        self.assertEquals(actual_stat, expected)
        self.assertEquals(response['result'].get('Blood Group').get('field_type'), 'select1')

    def test_get_stats_with_date_filters(self):
        data = {"search_filters": "{\"search_text\":\"\",\"dateQuestionFilters\":{\"q3\":\"10.03.2014 - 10.05.2014\", \"q4\":\"01.2015 - 02.2015\" }}"}

        res = self.client.post("/project/submissions/%s/analysis" % form_code, data)

        expected = set([(1, "A"), (1, "B"), (0, "AB"), (0, "O")])
        response = json.loads(res.content)
        actual_stat = set([(i["count"], i["term"]) for i in response['result'].get('Blood Group').get('data')])
        self.assertEquals(actual_stat, expected)
        self.assertEquals(response['result'].get('Blood Group').get('field_type'), 'select1')




