import unittest
from elasticutils import S, DictSearchResults

from mock import Mock, patch, PropertyMock, MagicMock
from datawinners.search.submission_index import es_field_name

from datawinners.search.submission_query import SubmissionQuery, SubmissionQueryResponseCreator
from mangrove.form_model.field import Field
from mangrove.form_model.form_model import FormModel


class TestSubmissionQuery(unittest.TestCase):
    def test_should_return_submission_log_specific_header_fields(self):
        form_model = Mock(spec=FormModel, id="2323")
        type(form_model).entity_type = PropertyMock(return_value=["clinic"])
        entity_question_field = Mock(spec=Field)
        type(form_model).entity_question = PropertyMock(return_value=entity_question_field)
        type(form_model).event_time_question = PropertyMock(return_value=None)
        entity_question_field.code.lower.return_value = 'eid'
        with patch("datawinners.search.submission_headers.header_fields") as header_fields:
            header_fields.return_value = {}

            headers = SubmissionQuery(form_model, {}).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in
                        ["ds_id", "ds_name", "date", "status", "eid", "entity_short_code"]]
            self.assertListEqual(expected, headers)

    def test_should_have_reporting_date_header_if_form_model_has_reporting_date(self):
        form_model = Mock(spec=FormModel, id="2323")
        type(form_model).entity_type = PropertyMock(return_value=["clinic"])
        entity_question_field = Mock(spec=Field)
        type(form_model).entity_question = PropertyMock(return_value=entity_question_field)
        entity_question_field.code.lower.return_value = 'eid'

        event_time_field = Mock(spec=Field)
        type(form_model).event_time_question = PropertyMock(return_value=event_time_field)
        event_time_field.code.lower.return_value = "rp_date"

        with patch("datawinners.search.submission_headers.header_fields") as header_fields:
            header_fields.return_value = {}

            headers = SubmissionQuery(form_model, {}).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in
                        ["ds_id", "ds_name", "date", "status", "eid", "entity_short_code", "rp_date"]]
            self.assertListEqual(expected, headers)

    def test_submission_status_headers_for_success_and_erred_submissions(self):
        form_model = Mock(spec=FormModel, id="2323")
        type(form_model).entity_type = PropertyMock(return_value=["clinic"])
        entity_question_field = Mock(spec=Field)
        type(form_model).entity_question = PropertyMock(return_value=entity_question_field)
        type(form_model).event_time_question = PropertyMock(return_value=None)
        entity_question_field.code.lower.return_value = 'eid'
        with patch("datawinners.search.submission_headers.header_fields") as header_fields:
            header_fields.return_value = {}
            query_params = {"filter": "success"}

            headers = SubmissionQuery(form_model, query_params).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in ["ds_id", "ds_name", "date", "eid", "entity_short_code"]]
            self.assertListEqual(expected, headers)

            query_params = {"filter": "error"}

            headers = SubmissionQuery(form_model, query_params).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in
                        ["ds_id", "ds_name", "date", "error_msg", "eid", "entity_short_code"]]
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