import json
from django.test import TestCase, Client
from datawinners.alldata.views import get_project_info
from datawinners.feeds.migrate import project_by_form_model_id
from datawinners.main.database import get_db_manager
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.utils.json_codecs import decode_json


class TestDeleteSubmission(TestCase):
    def setUp(self):
        self.client = Client()
        self.create_submissions()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

        self.dbm = get_db_manager('hni_testorg_slx364903')

    def test_should_delete_all_submissions_given_delete_all_flag_true(self):
        self.create_submissions()
        project = self.project_info('cli001')
        resp = self.client.post('/project/' + project.id + '/submissions/delete/',
                                {'all_selected': 'true', 'submission_type': 'all', 'search_filters': "{\"search_text\":\"unique\"}"})

        self.assertEqual(json.loads(resp.content)['success'], True)

    def create_submissions(self):
        _from = "917798987116"
        _to = "919880734937"
        for i in range(1, 5):
            message = "cli001 cid001 unique%s %d 02.02.2012 a a 2,2 a" % (i, i)
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
            self.client.post("/submission", data)


    def project_info(self, form_code):
        form_model = get_form_model_by_code(self.dbm, form_code)
        project = project_by_form_model_id(self.dbm, form_model.id)
        return project