import json

from django.test import Client
from django.utils import unittest
from mock import Mock, PropertyMock

from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import SelectField
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from datawinners.project.views.submission_views import create_statistics_response


class TestAnalysisStats(unittest.TestCase):
    def test_get_stats(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        data = {"search_filters": "{\"search_text\":\"Shweta\"}"}
        res = self.client.post("/project/submissions/cli018/analysis", data)
        expected = [{"count": 3, "term": "b+"}, {"count": 2, "term": "o+"}, {"count": 1, "term": "o-"},
                    {"count": 1, "term": "ab"}]
        response = json.loads(res.content)
        self.assertEquals(response['result'].get('What is your blood group?').get('data'), expected)
        self.assertEquals(response['result'].get('What is your blood group?').get('field_type'), 'select1')

    def test_should_contain_count_zero_for_options_with_no_submissions(self):
        facet_results = {
        '0dab4170697411e3985908002738abcf_bg_value': [{'count': 3, 'term': 'b+'}, {'count': 2, 'term': 'o+'}]}

        form_model = Mock(spec=FormModel)
        type(form_model).id = PropertyMock(return_value='0dab4170697411e3985908002738abcf')
        form_model._get_field_by_code.return_value = SelectField(name="What is your blood group", code="BG",
                                                                 label="What is your blood group?",
                                                                 options=[{"text": "O+"}, {"text": "B+"},
                                                                          {"text": "A-"}], single_select_flag=False,
                                                                 ddtype=DataDictType(Mock(DatabaseManager)),
                                                                 required=False)

        analysis_response = create_statistics_response(facet_results, form_model)
        self.assertIn({'count': 0, 'term': 'a-'}, analysis_response["What is your blood group?"].get('data'))


