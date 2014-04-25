import unittest
from mock import MagicMock, Mock
from datawinners.search.index_utils import es_field_name
from datawinners.search.submission_headers import SubmissionAnalysisHeader, AllSubmissionHeader, SuccessSubmissionHeader, ErroredSubmissionHeader, HeaderFactory
from mangrove.form_model.field import TextField, IntegerField, UniqueIdField
from mangrove.form_model.form_model import FormModel


class TestSubmissionHeader(unittest.TestCase):
    def setUp(self):
        self.field1 = TextField('text', 'q1', 'Enter Text')
        self.field2 = IntegerField('integer', 'q2', 'Enter a Number')
        self.field3 = UniqueIdField('clinic', 'unique_id_field', 'q3', 'Which clinic are you reporting on')
        self.field4 = UniqueIdField('school', 'unique_id_field2', 'q4', 'Which school are you reporting on')
        self.form_model = MagicMock(spec=FormModel)
        self.form_model.id = 'form_model_id'

    def test_get_header_dict_from_form_model_without_unique_id_question(self):
        self.form_model.fields = [self.field1, self.field2]
        self.form_model.entity_questions = []
        expected = {'date': 'Submission Date', 'ds_id': 'Datasender Id', 'ds_name': 'Data Sender',
                    'form_model_id_q1': 'Enter Text', 'form_model_id_q2': 'Enter a Number'}

        result = SubmissionAnalysisHeader(self.form_model).get_header_dict()

        self.assertDictEqual(expected, result)

    def test_get_header_dict_from_form_model_with_single_unique_id_question(self):
        self.form_model.fields = [self.field1, self.field2, self.field3]
        self.form_model.entity_questions = [self.field3]
        expected = {'date': 'Submission Date', 'ds_id': 'Datasender Id', 'ds_name': 'Data Sender',
                    'form_model_id_q1': 'Enter Text', 'form_model_id_q2': 'Enter a Number',
                    'form_model_id_q3': 'Which clinic are you reporting on',
                    'form_model_id_q3_unique_code': 'clinic ID'}

        result = SubmissionAnalysisHeader(self.form_model).get_header_dict()

        self.assertDictEqual(expected, result)

    def test_should_return_submission_log_specific_header_fields(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]

        headers = AllSubmissionHeader(self.form_model).get_header_field_names()

        expected = [es_field_name(f, self.form_model.id) for f in
                    ["ds_id", "ds_name", "date", "status", "q1", "q2", "q3", "q3_unique_code", "q4", "q4_unique_code"]]
        self.assertListEqual(expected, headers)


    def test_submission_status_headers_for_success_submissions(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]

        headers = SuccessSubmissionHeader(self.form_model).get_header_field_names()

        expected = [es_field_name(f, self.form_model.id) for f in
                    ["ds_id", "ds_name", "date", "q1", "q2", "q3", "q3_unique_code", "q4", "q4_unique_code"]]
        self.assertListEqual(expected, headers)

    def test_submission_status_headers_for_errored_submissions(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]

        headers = ErroredSubmissionHeader(self.form_model).get_header_field_names()

        expected = [es_field_name(f, self.form_model.id) for f in
                    ["ds_id", "ds_name", "date","error_msg", "q1", "q2", "q3", "q3_unique_code", "q4", "q4_unique_code"]]
        self.assertListEqual(expected, headers)


class TestHeaderFactory(unittest.TestCase):
    def test_should_return_header_instance_based_on_submission_type(self):
        form_model = Mock(spec=FormModel)
        self.assertIsInstance(HeaderFactory(form_model).create_header("all"), AllSubmissionHeader)
        self.assertIsInstance(HeaderFactory(form_model).create_header("success"), SuccessSubmissionHeader)
        self.assertIsInstance(HeaderFactory(form_model).create_header("error"), ErroredSubmissionHeader)
        self.assertIsInstance(HeaderFactory(form_model).create_header("analysis"), SubmissionAnalysisHeader)