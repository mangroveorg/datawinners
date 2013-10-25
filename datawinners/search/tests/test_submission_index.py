import unittest
from datawinners.search.submission_index import _update_with_form_model_fields
from mangrove.datastore.documents import EnrichedSurveyResponseDocument


class TestSubmissionIndex(unittest.TestCase):

    def test_should_update_search_dict_with_form_field_questions_for_success_submissions(self):
        search_dict = {}
        values = {'eid':{'answer': {'deleted': False, 'id': u'cid005', 'name': 'Test'}, 'is_entity_question': 'true'},
                  'q2': {'answer': 'name', 'type': 'text', 'label': 'First Name'},
                  'q3': {'answer': {u'b': 'two', u'c': 'three'}, 'type': 'select', 'label': 'Question 2'},
                  'q4': {'answer': '3,3', 'type': 'geocode', 'label': 'gps'},
                  'q5': {'answer': '11.12.2012', 'format': 'mm.dd.yyyy', 'type': 'date', 'label': 'date'}}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="success")
        _update_with_form_model_fields(submission_doc, search_dict)
        self.assertEquals({'eid':'Test','q2': 'name', 'q3': 'three,two', 'q4': '3,3', 'q5': '11.12.2012'}, search_dict)

    def test_should_update_search_dict_with_form_field_questions_for_error_submissions(self):
        search_dict = {}
        values = {'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="error")
        _update_with_form_model_fields(submission_doc, search_dict)
        self.assertEquals({'q2': 'wrong number', 'q3': 'wrong text'}, search_dict)
