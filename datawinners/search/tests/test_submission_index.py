import unittest
import elasticutils
from mangrove.transport.contract.survey_response import SurveyResponse
from mock import Mock, PropertyMock, patch, MagicMock
from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from datawinners.search.submission_query import SubmissionQueryBuilder
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField, Field, GeoCodeField, SelectField, DateField, UniqueIdField
from mangrove.form_model.form_model import FormModel
from datawinners.search.submission_index import _update_with_form_model_fields, update_submission_search_for_subject_edition
from mangrove.datastore.documents import EnrichedSurveyResponseDocument, SurveyResponseDocument, DocumentBase, FormModelDocument


class TestSubmissionIndex(unittest.TestCase):
    def setUp(self):
        self.form_model = MagicMock(spec=FormModel, id="1212")
        self.field1 = UniqueIdField(unique_id_type='clinic', name='unique_id', code="q1", label='which clinic')
        self.field2 = TextField('text', "q2", "enter text")
        self.field3 = GeoCodeField('gps', "q3", "enter gps")
        self.field4 = SelectField('select', 'q4', 'enter one',
                                  [{'text': 'one', 'val': 'a'}, {'text': 'two', 'val': 'b'}], single_select_flag=False)
        self.field5 = DateField('date', 'q5', 'enter date', 'mm.dd.yyyy')

    def test_should_update_search_dict_with_form_field_questions_for_success_submissions(self):
        search_dict = {}
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4, self.field5]
        values = {'q1': 'cid005',
                  'q2': "name",
                  'q3': "3,3",
                  'q4': "ab",
                  'q5': '11.12.2012'}
        submission_doc = SurveyResponseDocument(values=values, status="success")
        self.form_model.get_field_by_code_and_rev.return_value = self.field4
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'clinic1'

            _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)

            self.assertEquals(
                {'1212_q1': 'clinic1', "1212_q1_unique_code": "cid005", '1212_q2': 'name', '1212_q3': '3,3',
                 '1212_q4': ['one', 'two'],
                 '1212_q5': '11.12.2012', 'void': False}, search_dict)

    def test_should_update_search_dict_with_form_field_questions_for_error_submissions(self):
        search_dict = {}
        self.form_model.fields = [self.field1, self.field2, self.field3]
        values = {'q1': 'test_id', 'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="error")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'test1'
            _update_with_form_model_fields(None, submission_doc, search_dict, self.form_model)
            self.assertEquals(
                {'1212_q1': 'test1', "1212_q1_unique_code": "test_id", '1212_q2': 'wrong number',
                 '1212_q3': 'wrong text',
                 'void': False},
                search_dict)

    def test_should_update_search_dict_with_none_for_missing_entity_answer_in_submission(self):
        search_dict = {}
        self.form_model.fields = [self.field1, self.field2, self.field3]
        values = {'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = SurveyResponseDocument(values=values, status="error")
        _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
        self.assertEquals(
            {'1212_q1': 'N/A', "1212_q1_unique_code": 'N/A', '1212_q2': 'wrong number', '1212_q3': 'wrong text',
             'void': False},
            search_dict)

    def test_should_update_submission_index_date_field_with_current_format(self):
        self.form_model.fields = [self.field1, self.field5]
        values = {'q1': 'cid005',
                  'q5': '12.2012'}
        submission_doc = SurveyResponseDocument(values=values, status="success", form_model_revision="rev1")
        search_dict = {}
        self.form_model._doc = Mock(spec=FormModelDocument)
        self.form_model._doc.rev = "rev2"
        self.form_model.get_field_by_code_and_rev.return_value = DateField("q5", "date", "Date", "mm.yyyy")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'Test'
            search_dict = _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict,
                                                         self.form_model)
            self.assertEquals("12.01.2012", search_dict.get("1212_q5"))


    def test_should_update_entity_field_in_submission_index(self):
        entity_doc = MagicMock(spec=Entity)
        dbm = MagicMock(spec=DatabaseManager)
        data = {'name': {'value': 'bangalore'}}
        dbm.database_name = 'db_name'
        entity_doc.entity_type = ['clinic']
        entity_doc.short_code = 'cli001'
        entity_doc.data = data
        with patch.object(SubmissionQueryBuilder, 'query_all') as query_all:
            with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
                load_all_rows_in_view.return_value = [{'value': {'name': "project name", "form_code": "cli001",
                                                                 "json_fields": [
                                                                     {"name": "unique_id_field", "type": "unique_id",
                                                                      "unique_id_type": 'clinic', "code": 'q1'}],
                                                                 "_id": "form_model_id"}}]
                survey_response_index1 = Mock(_id='id1')
                filtered_query = Mock(spec=elasticutils.S)
                filtered_query.all.return_value = [survey_response_index1]

                query_all.return_value = filtered_query

                with patch.object(SubmissionIndexUpdateHandler,
                                  'update_field_in_submission_index') as update_field_in_submission_index:
                    update_submission_search_for_subject_edition(entity_doc, dbm)

                    query_all.assert_called_with('db_name', 'form_model_id',
                                                 **{'form_model_id_q1_unique_code': 'cli001'})
                    update_field_in_submission_index.assert_called_with('id1', {'form_model_id_q1': 'bangalore'})