import json
import unittest
import uuid

from django.test import Client
from nose.plugins.attrib import attr
from mangrove.form_model.form_model import get_form_model_by_code

from datawinners.main.database import get_db_manager
from datawinners.project.models import project_by_form_model_id
from datawinners.search.submission_query import SubmissionQuery
from framework.utils.common_utils import random_string


@attr('functional_test')
class TestDeleteSubmission(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

        self.dbm = get_db_manager('hni_testorg_slx364903')
        self.form_model = self.project_info('cli001')

    def test_should_delete_all_submissions_given_delete_all_flag_true(self):
        unique_text = random_string()
        self.create_success_submissions(2, unique_text)
        self.create_errorred_submissions(1, unique_text)
        self.assertEqual(len(self.get_submissions('all', unique_text)), 3)

        resp = self.client.post('/project/' + self.form_model.id + '/submissions/delete/',
                                {'all_selected': 'true', 'submission_type': 'all',
                                 'search_filters': json.dumps({'search_text': unique_text,
                                                                "dateQuestionFilters":{}
                                                              })
                                })

        self.assertEqual(json.loads(resp.content)['success'], True)
        self.assertEqual(len(self.get_submissions('all', unique_text)), 0)

    def test_should_delete_only_success_submissions_given_delete_all_flag_true_and_submission_type_success(self):
        unique_text = random_string()
        self.create_success_submissions(2, unique_text)
        self.create_errorred_submissions(1, unique_text)
        self.assertEqual(len(self.get_submissions('success', unique_text)), 2)

        resp = self.client.post('/project/' + self.form_model.id + '/submissions/delete/',
                                {'all_selected': 'true', 'submission_type': 'success',
                                 'search_filters': json.dumps({'search_text': unique_text,
                                                                "dateQuestionFilters":{}})})

        self.assertEqual(json.loads(resp.content)['success'], True)
        self.assertEqual(len(self.get_submissions('success', unique_text)), 0)
        self.assertEqual(len(self.get_submissions('error', unique_text)), 1)

    def create_success_submissions(self, num_of_submissions, unique_text):
        _from = "917798987116"
        _to = "919880734937"
        for i in range(0, num_of_submissions):
            message = "cli001 cid001 %s 4%s 02.02.2012 a a 2,2 a" % (unique_text, i)
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id":uuid.uuid1().hex}
            self.client.post("/submission", data)

    def create_errorred_submissions(self, num_of_submissions, unique_text):
        _from = "917798987116"
        _to = "919880734937"
        for i in range(0, num_of_submissions):
            message = "cli001 cid001 %s %s 02.02.2012 a a 2,2 a" % (unique_text, i)
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id":uuid.uuid1().hex}
            self.client.post("/submission", data)

    def get_submissions(self, filter_type, search_text):
        query_params = {'search_filters': {'search_text': search_text,"dateQuestionFilters":{}}}
        query_params.update({'filter': filter_type})
        submissions = SubmissionQuery(self.form_model, query_params).query(self.dbm.database_name)
        return submissions

    def project_info(self, form_code):
        return get_form_model_by_code(self.dbm, form_code)