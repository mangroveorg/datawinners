import unittest
import elasticutils
from mock import Mock, PropertyMock, patch
from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from datawinners.search.submission_query import SubmissionQueryBuilder
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField, Field, GeoCodeField, SelectField
from mangrove.form_model.form_model import FormModel
from datawinners.search.submission_index import _update_with_form_model_fields, update_submission_search_for_subject_edition
from mangrove.datastore.documents import EnrichedSurveyResponseDocument, SurveyResponseDocument


class TestSubmissionIndex(unittest.TestCase):
    def setUp(self):
        self.form_model = Mock(spec=FormModel, id="1212")
        #mock_field = Mock(TextField)
        #mock_field.is_entity_field = True
        #mock_field.code = 'EID'
        #mock_field.type="text"
        self.form_model.fields = [Mock(spec=Field, is_entity_field=True, code="EID", type="text"),
                                  Mock(spec=Field, is_entity_field=False, code="q2", type="text"),
                                  Mock(spec=Field, is_entity_field=False, code="q3", type="text")]

    def test_should_update_search_dict_with_form_field_questions_for_success_submissions(self):
        search_dict = {}
        self.form_model.fields.append(Mock(spec=Field, is_entity_field=False, code="q4", type="select",
                                           get_option_value_list=Mock(return_value=["one", "two"])))
        self.form_model.fields.append(Mock(spec=Field, is_entity_field=False, code="q5", type="text"))
        values = {'eid': 'cid005',
                  'q2': "name",
                  'q3': "3,3",
                  'q4': "ab",
                  'q5': '11.12.2012'}
        submission_doc = SurveyResponseDocument(values=values, status="success")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'Test'
            _update_with_form_model_fields(None, submission_doc, search_dict, self.form_model)
            self.assertEquals(
                {'1212_eid': 'Test', "entity_short_code": "cid005", '1212_q2': 'name', '1212_q3': '3,3',
                 '1212_q4': ['one', 'two'],
                 '1212_q5': '11.12.2012', 'void': False}, search_dict)

    def test_should_update_search_dict_with_null_values_for_missing_field_in_submission(self):
        search_dict = {}
        form_model_id = '12121'
        field1 = TextField(name='entity_question', code='eid', label='eid', ddtype=Mock(spec=DataDictType),
                           entity_question_flag=True)
        field2 = TextField(name='text', code='q2', label='name', ddtype=Mock(spec=DataDictType))
        field3 = GeoCodeField(name='geo_code', code='q3', label='geo_code', ddtype=Mock(spec=DataDictType))
        field4 = SelectField(name='multi_select', code='q4', label='mul_sel',
                             options=[("one", "a"), ("two", "b"), ("three", "c")], ddtype=Mock(spec=DataDictType),
                             single_select_flag=False)
        field5 = SelectField(name='single_select', code='q5', label='sin_sel',
                             options=[("hi", "a"), ("hello", "b"), ("hru", "c")], ddtype=Mock(spec=DataDictType))
        form_model = Mock(spec=FormModel, id=form_model_id, fields=[field1, field2, field3, field4, field5],
                          name="test_form_model")

        values = {'eid': 'cid005',
                  'q2': "name",
                  'q3': "3,3",
                  'q100': "ab",
                  'q5': 'a'}
        submission_doc = SurveyResponseDocument(values=values, status="success")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'Test'

            _update_with_form_model_fields(None, submission_doc, search_dict, form_model)

            self.assertEquals(
                {form_model_id + '_eid': 'Test', "entity_short_code": "cid005", form_model_id + '_q2': 'name',
                 form_model_id + '_q3': '3,3', form_model_id + '_q4': [],
                 form_model_id + '_q5': 'hi', 'void': False}, search_dict)

    def test_should_update_search_dict_with_form_field_questions_for_error_submissions(self):
        search_dict = {}
        values = {'eid': 'test_id', 'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="error")
        with patch('datawinners.search.submission_index.lookup_entity_name') as lookup_entity_name:
            lookup_entity_name.return_value = 'Test'
            _update_with_form_model_fields(None, submission_doc, search_dict, self.form_model)
            self.assertEquals(
                {'1212_eid': 'Test', "entity_short_code": "test_id", '1212_q2': 'wrong number', '1212_q3': 'wrong text',
                 'void': False},
                search_dict)

    def test_should_update_search_dict_with_none_for_missing_entity_answer_in_submission(self):
        search_dict = {}
        values = {'q2': 'wrong number', 'q3': 'wrong text'}
        submission_doc = EnrichedSurveyResponseDocument(values=values, status="error")
        _update_with_form_model_fields(Mock(spec=DatabaseManager), submission_doc, search_dict, self.form_model)
        self.assertEquals(
            {'1212_eid': 'NA', "entity_short_code": 'NA', '1212_q2': 'wrong number', '1212_q3': 'wrong text',
             'void': False},
            search_dict)

    def test_should_update_entity_field_in_submission_index(self):
        entity_doc = Mock(spec=Entity)
        dbm = Mock(spec=DatabaseManager)
        data = {'name': {'value': 'bangalore'}}
        type(dbm).database_name = PropertyMock(return_value='db_name')
        type(entity_doc).entity_type = PropertyMock(return_value=['Clinic'])
        type(entity_doc).short_code = PropertyMock(return_value='cli001')
        type(entity_doc).data = PropertyMock(return_value=data)

        with patch(
                'datawinners.search.submission_index._get_form_models_from_projects') as get_form_models_from_projects:
            with patch.object(SubmissionQueryBuilder, 'query_all') as query_all:
                form_model1 = Mock(spec=FormModel, id='12345')
                entity_name = Mock()
                type(entity_name).code = PropertyMock(return_value='q1')
                type(form_model1).entity_question = PropertyMock(return_value=entity_name)
                get_form_models_from_projects.return_value = [form_model1]
                with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
                    load_all_rows_in_view.return_value = []
                    survey_response_index1 = Mock(_id='id1')
                    filtered_query = Mock(spec=elasticutils.S)
                    filtered_query.all.return_value = [survey_response_index1]

                    query_all.return_value = filtered_query

                    with patch.object(SubmissionIndexUpdateHandler,
                                      'update_field_in_submission_index') as update_field_in_submission_index:
                        update_submission_search_for_subject_edition(entity_doc, dbm)
                        query_all.assert_called_with('db_name', '12345',**{'entity_short_code': 'cli001'})
                        update_field_in_submission_index.assert_called_with('id1', {'12345_q1': 'bangalore'})