import unittest

from mock import Mock, patch, PropertyMock
from datawinners.search.submission_index import es_field_name

from datawinners.search.submission_query import SubmissionQuery
from mangrove.form_model.field import Field
from mangrove.form_model.form_model import FormModel


class TestSubmissionQuery(unittest.TestCase):

    def test_should_return_submission_log_specific_header_fields(self):
        form_model = Mock(spec=FormModel,id="2323")
        type(form_model).entity_type = PropertyMock(return_value = ["clinic"])
        entity_question_field = Mock(spec=Field)
        type(form_model).entity_question = PropertyMock(return_value =entity_question_field)
        type(form_model).event_time_question = PropertyMock(return_value =None)
        entity_question_field.code.lower.return_value = 'eid'
        with patch("datawinners.search.submission_query.header_fields") as header_fields:
            header_fields.return_value = {}

            headers = SubmissionQuery(form_model, {}).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in ["ds_id", "ds_name", "date", "status", "eid","entity_short_code"]]
            self.assertListEqual(expected, headers)

    def test_should_have_reporting_date_header_if_form_model_has_reporting_date(self):
        form_model = Mock(spec=FormModel, id="2323")
        type(form_model).entity_type = PropertyMock(return_value = ["clinic"])
        entity_question_field = Mock(spec=Field)
        type(form_model).entity_question = PropertyMock(return_value =entity_question_field)
        entity_question_field.code.lower.return_value = 'eid'

        event_time_field = Mock(spec=Field)
        type(form_model).event_time_question = PropertyMock(return_value =event_time_field)
        event_time_field.code.lower.return_value = "rp_date"

        with patch("datawinners.search.submission_query.header_fields") as header_fields:
            header_fields.return_value = {}

            headers = SubmissionQuery(form_model, {}).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in ["ds_id", "ds_name", "date", "status", "eid","entity_short_code" ,"rp_date"]]
            self.assertListEqual(expected, headers)

    def test_submission_status_headers_for_success_and_erred_submissions(self):
        form_model = Mock(spec=FormModel,id="2323")
        type(form_model).entity_type = PropertyMock(return_value = ["clinic"])
        entity_question_field = Mock(spec=Field)
        type(form_model).entity_question = PropertyMock(return_value=entity_question_field)
        type(form_model).event_time_question = PropertyMock(return_value =None)
        entity_question_field.code.lower.return_value = 'eid'
        with patch("datawinners.search.submission_query.header_fields") as header_fields:
            header_fields.return_value = {}
            query_params = {"filter": "success"}

            headers = SubmissionQuery(form_model, query_params).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in ["ds_id", "ds_name", "date", "eid","entity_short_code"]]
            self.assertListEqual(expected, headers)

            query_params = {"filter": "error"}

            headers = SubmissionQuery(form_model, query_params).get_headers(Mock, "code")

            expected = [es_field_name(f, "2323") for f in ["ds_id", "ds_name", "date", "error_msg", "eid","entity_short_code"]]
            self.assertListEqual(expected, headers)