import unittest
from elasticutils import S, DictSearchResults

from mock import Mock, patch, PropertyMock, MagicMock
from datawinners.search.index_utils import es_field_name

from datawinners.search.submission_query import SubmissionQuery, SubmissionQueryResponseCreator
from mangrove.form_model.field import Field
from mangrove.form_model.form_model import FormModel
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


class TestSubmissionQuery(unittest.TestCase):
    def setUp(self):
        self.form_model = MagicMock(spec=FormModel, id="2323")
        self.form_model.entity_type = ["clinic"]
        entity_question_field = Field(code='eid')
        self.form_model.entity_question = entity_question_field
        self.patcher = patch("datawinners.search.submission_headers.header_fields")
        header_fields_patcher = self.patcher.start()
        header_fields_patcher.return_value = {"eid": "which clinic"}

    def tearDown(self):
        self.patcher.stop()

    def test_should_return_submission_log_specific_header_fields(self):
        query_params = {"filter": "all"}

        headers = SubmissionQuery(self.form_model, query_params).get_headers()

        expected = [es_field_name(f, "2323") for f in
                    ["ds_id", "ds_name", "date", "status", "eid", "entity_short_code"]]
        self.assertListEqual(expected, headers)


    def test_submission_status_headers_for_success_and_erred_submissions(self):
        query_params = {"filter": "success"}

        headers = SubmissionQuery(self.form_model, query_params).get_headers()

        expected = [es_field_name(f, "2323") for f in ["ds_id", "ds_name", "date", "eid", "entity_short_code"]]
        self.assertListEqual(expected, headers)

        query_params = {"filter": "error"}

        headers = SubmissionQuery(self.form_model, query_params).get_headers()

        expected = [es_field_name(f, "2323") for f in
                    ["ds_id", "ds_name", "date", "error_msg", "eid", "entity_short_code"]]
        self.assertListEqual(expected, headers)

    def test_headers_for_submission_analysis(self):
        query_params = {"filter": "analysis"}

        headers = SubmissionQuery(self.form_model, query_params).get_headers()

        expected = [es_field_name(f, "2323") for f in
                    ["date", "ds_id", "ds_name", "eid", "entity_short_code"]]
        self.assertListEqual(expected, headers)


class TestSubmissionResponseCreator(unittest.TestCase):
    def test_should_append_styling_for_datasender_and_subject_ids(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['ds_id', 'ds_name', 'entity_short_code', 'entity_question']
        query = Mock()
        dict_result = DictSearchResults('', {}, [{'_id': 'index_id',
                                                  '_source': {'ds_id': 'some_id', 'ds_name': 'his_name',
                                                              'entity_short_code': 'subject_id',
                                                              'entity_question': 'sub_last_name'}}], '')
        query.values_dict.return_value = dict_result
        form_model.entity_question = Mock(code='entity_question')

        submissions = SubmissionQueryResponseCreator(form_model).create_response(required_field_names, query)

        expected = [['index_id', ["his_name<span class='small_grey'>  some_id</span>"],
                     ["sub_last_name<span class='small_grey'>  subject_id</span>"]]]
        self.assertEqual(submissions, expected)

    def test_should_give_back_none_for_no_entry_for_datasender_or_subject_ids(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['ds_id', 'ds_name', 'entity_short_code', 'entity_question', 'some_question']
        query = Mock()
        dict_result = DictSearchResults('', {}, [{'_id': 'index_id',
                                                  '_source': {'some_question': 'answer'}}], '')
        query.values_dict.return_value = dict_result
        form_model.entity_question = Mock(code='q1')

        submissions = SubmissionQueryResponseCreator(form_model).create_response(required_field_names, query)

        expected = [['index_id', None, None, 'answer']]
        self.assertEqual(submissions, expected)

    def test_should_give_back_entries_according_to_header_order(self):
        form_model = MagicMock(spec=FormModel)
        required_field_names = ['some_question', 'ds_id', 'ds_name', 'entity_short_code', 'entity_question']
        query = Mock()
        dict_result = DictSearchResults('', {}, [{'_id': 'index_id',
                                                  '_source': {'ds_id': 'some_id', 'ds_name': 'his_name',
                                                              'entity_short_code': 'subject_id',
                                                              'entity_question': 'sub_last_name',
                                                              'some_question': 'answer for it'}}], '')
        query.values_dict.return_value = dict_result
        form_model.entity_question = Mock(code='entity_question')

        submissions = SubmissionQueryResponseCreator(form_model).create_response(required_field_names, query)

        expected = [['index_id', 'answer for it', ["his_name<span class='small_grey'>  some_id</span>"],
                     ["sub_last_name<span class='small_grey'>  subject_id</span>"]]]
        self.assertEqual(submissions, expected)
