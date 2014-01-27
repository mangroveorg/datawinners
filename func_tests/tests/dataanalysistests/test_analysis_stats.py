import json
from nose.plugins.attrib import attr

from datawinners.project.views.submission_views import create_statistics_response
from django.test import Client
from django.utils import unittest
from django.utils.unittest.case import SkipTest
from mock import Mock, MagicMock

from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import SelectField
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel

@attr('functional_test')
class TestAnalysisStats(unittest.TestCase):
    def test_get_stats(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        data = {"search_filters": "{\"search_text\":\"Shweta\"}"}
        res = self.client.post("/project/submissions/cli018/analysis", data)
        expected = [{"count": 3, "term": "B+"}, {"count": 2, "term": "O+"}, {"count": 1, "term": "O-"},
                    {"count": 1, "term": "AB"}]
        response = json.loads(res.content)
        self.assertEquals(response['result'].get('What is your blood group?').get('data'), expected)
        self.assertEquals(response['result'].get('What is your blood group?').get('field_type'), 'select1')



class TestSubmissionAnalysisResponseCreation(unittest.TestCase):
    def test_should_contain_count_zero_for_options_with_no_submissions(self):
        facet_results = [{
            'es_field_name': '0dab4170697411e3985908002738abcf_q1_value',
            'facets': [{'count': 3, 'term': 'B+'}, {'count': 2, 'term': 'O+'}],
            'total': 6
        }]

        form_model = MagicMock(spec=FormModel)
        form_model.id = '0dab4170697411e3985908002738abcf'
        form_model._get_field_by_code.return_value = SelectField(name="What is your blood group", code="BG",
                                                                 label="What is your blood group?",
                                                                 options=[{"text": "O+"}, {"text": "B+"},
                                                                          {"text": "A-"}], single_select_flag=False,
                                                                 ddtype=DataDictType(Mock(DatabaseManager)),
                                                                 required=False)

        analysis_response = create_statistics_response(facet_results, form_model)

        self.assertIn({'count': 0, 'term': 'A-'}, analysis_response["What is your blood group?"].get('data'))

    def test_should_create_result_with_facet_values(self):
        facet_results = [{
            'es_field_name': '0dab4170697411e3985908002738abcf_q1_value',
            'facets': [{'count': 3, 'term': 'B+'}, {'count': 2, 'term': 'O+'}],
            'total': 6
        }]

        form_model = MagicMock(spec=FormModel)
        form_model.id = '0dab4170697411e3985908002738abcf'
        form_model._get_field_by_code.return_value = SelectField(name="What is your blood group", code="BG",
                                                                 label="What is your blood group?",
                                                                 options=[{"text": "O+"}, {"text": "B+"}], single_select_flag=False,
                                                                 ddtype=DataDictType(Mock(DatabaseManager)),
                                                                 required=False)

        analysis_response = create_statistics_response(facet_results, form_model)

        self.assertTrue("What is your blood group?" in analysis_response)
        facet_result = analysis_response["What is your blood group?"]
        self.assertEqual(facet_result['count'], 6)
        self.assertEqual(facet_result['data'], [{'term': 'B+', 'count': 3}, {'term': 'O+', 'count': 2}])
        self.assertEqual(facet_result['field_type'], 'select')




