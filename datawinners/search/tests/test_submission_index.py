import unittest
from mock import Mock
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from datawinners.search.submission_index import _update_with_form_model_fields
from mangrove.datastore.documents import EnrichedSurveyResponseDocument


class TestSubmissionIndex(unittest.TestCase):
    def setUp(self):
        self.form_model = Mock(FormModel)
        mock_field = Mock(TextField)
        mock_field.is_entity_field = True
        mock_field.code = 'EID'
        self.form_model.fields = [mock_field]

    def test_should_update_search_dict_with_form_field_questions_for_success_submissions(self):

        search_dict = {}
        values = {'eid': {'answer': {'deleted': False, 'id': 'cid005', 'name': 'Test'}, 'is_entity_question': 'true'},
                  'q2': {'answer': 'name', 'type': 'text', 'label': 'First Name'},
                  'q3': {'answer': {u'b': 'two', u'c': 'three'}, 'type': 'select', 'label': 'Question 2'},
                  'q4': {'answer': '3,3', 'type': 'geocode', 'label': 'gps'},
                  'q5': {'answer': '11.12.2012', 'format': 'mm.dd.yyyy', 'type': 'date', 'label': 'date'}}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="success")
        _update_with_form_model_fields(None, submission_doc, search_dict, self.form_model)
        self.assertEquals({'eid': 'Test', "entity_short_code": "cid005", 'q2': 'name', 'q3': 'three,two', 'q4': '3,3',
                           'q5': '11.12.2012', 'void': False}, search_dict)

    def test_should_update_search_dict_with_form_field_questions_for_error_submissions(self):
        search_dict = {}
        values = {'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="error")
        _update_with_form_model_fields(None, submission_doc, search_dict, self.form_model)
        self.assertEquals({'q2': 'wrong number', 'q3': 'wrong text', 'void': False}, search_dict)
