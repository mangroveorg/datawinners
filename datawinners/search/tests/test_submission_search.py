import unittest
from elasticutils import S, DictSearchResults

from mock import Mock, patch, PropertyMock, MagicMock
from datawinners.search.index_utils import es_field_name

from datawinners.search.submission_query import SubmissionQuery, SubmissionQueryResponseCreator
from mangrove.form_model.field import Field, UniqueIdField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


class TestSubmissionResponseCreator(unittest.TestCase):
    def test_should_give_back_entries_according_to_header_order(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['some_question', 'ds_id', 'ds_name', 'form_model_id_q1', 'form_model_id_q1_unique_code']
        query = Mock()
        dict_result = DictSearchResults('', {}, [{'_id': 'index_id',
                                                  '_source': {'ds_id': 'his_id', 'ds_name': 'his_name',
                                                              'form_model_id_q1_unique_code': 'subject_id',
                                                              'form_model_id_q1': 'sub_last_name',
                                                              'some_question': 'answer for it'}}], '')
        query.values_dict.return_value = dict_result
        form_model.entity_questions = [UniqueIdField('Test subject', 'name', 'q1', 'which subject')]
        form_model.id = 'form_model_id'

        submissions = SubmissionQueryResponseCreator(form_model).create_response(required_field_names, query)

        expected = [['index_id', 'answer for it', ["his_name<span class='small_grey'>  his_id</span>"],
                     ["sub_last_name<span class='small_grey'>  subject_id</span>"]]]
        self.assertEqual(submissions, expected)

    def test_should_give_create_response_with_no_unique_id_fields(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['ds_id', 'ds_name', 'some_question']
        query = Mock()
        dict_result = DictSearchResults('', {}, [{'_id': 'index_id',
                                                  '_source': {'ds_id': 'his_id', 'ds_name': 'his_name',
                                                              'some_question': 'answer'}}], '')
        query.values_dict.return_value = dict_result
        form_model.entity_questions = []
        form_model.id = 'form_model_id'
        submissions = SubmissionQueryResponseCreator(form_model).create_response(required_field_names, query)

        expected = [['index_id', ["his_name<span class='small_grey'>  his_id</span>"], 'answer']]
        self.assertEqual(submissions, expected)
