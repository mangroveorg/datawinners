import unittest

from mock import MagicMock, Mock, patch

from datawinners.search.submission_headers import SubmissionAnalysisHeader, AllSubmissionHeader, SuccessSubmissionHeader, ErroredSubmissionHeader, HeaderFactory
from mangrove.form_model.field import TextField, IntegerField, UniqueIdField, FieldSet
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.project import Project
from collections import OrderedDict


class TestSubmissionHeader(unittest.TestCase):
    def setUp(self):
        self.field1 = TextField('text', 'q1', 'Enter Text')
        self.field2 = IntegerField('integer', 'q2', 'Enter a Number')
        self.field3 = UniqueIdField('clinic', 'unique_id_field', 'q3', 'Which clinic are you reporting on')
        self.field4 = UniqueIdField('school', 'unique_id_field2', 'q4', 'Which school are you reporting on')
        self.repeat_field = FieldSet('repeat','repeat', 'repeat label', field_set=[self.field1, self.field4])
        self.form_model = MagicMock(spec=Project)
        self.form_model.id = 'form_model_id'
        self.patch_get_entity_type_info = patch('datawinners.entity.import_data.get_entity_type_info')
        self.get_entity_type_info_mock = self.patch_get_entity_type_info.start()

    def tearDown(self):
        self.patch_get_entity_type_info.stop()

    def test_get_header_dict_from_form_model_without_unique_id_question(self):
        self.form_model.fields = [self.field1, self.field2]
        self.form_model.entity_questions = []
        
        expected = OrderedDict([('date', u'Submission Date'), ('datasender.id', u'Data Sender Id'),
            ('datasender.name', u'Data Sender Name'), ('datasender.mobile_number', u'Data Sender Mobile Number'),
            ('datasender.email', u'Data Sender Email'), ('datasender.location', u'Data Sender Location'),
            ('datasender.geo_code', u'Data Sender GPS Coordinates'),
            ('form_model_id_q1', 'text'), ('form_model_id_q2', 'integer')])

        result = SubmissionAnalysisHeader(self.form_model).get_header_dict()

        self.assertDictEqual(expected, result)

    def test_get_field_names_as_header_dict(self):
        self.get_entity_type_info_mock.return_value = dict(entity='clinic', code='cli002', names=['name1', 'name2'],
                                                          codes=['code1', 'code2'], labels=['label1','label2'], data=[])
        self.form_model.fields = [self.field1, self.field2, self.field3]
        self.form_model.entity_questions = [self.field3]
        expected = ['ds_id', 'ds_name','date',
                    'form_model_id_q1',
                    'form_model_id_q2',
                    'form_model_id_q3',
                    'form_model_id_q3_unique_code']

        result = AllSubmissionHeader(self.form_model).get_field_names_as_header_name()

        self.assertListEqual(expected, result)


    def test_get_header_dict_from_form_model_with_single_unique_id_question(self):
        self.get_entity_type_info_mock.return_value = dict(entity='clinic', code='cli002', names=['name1', 'name2'],
                                                          codes=['code1', 'code2'], labels=['label1','label2'], data=[])
        self.form_model.fields = [self.field1, self.field2, self.field3]
        self.form_model._dbm = Mock(spec=FormModel)
        self.form_model.entity_questions = [self.field3]
        expected = OrderedDict([('date', u'Submission Date'), ('datasender.id', u'Data Sender Id'),
            ('datasender.name', u'Data Sender Name'), ('datasender.mobile_number', u'Data Sender Mobile Number'),
            ('datasender.email', u'Data Sender Email'), ('datasender.location', u'Data Sender Location'),
            ('datasender.geo_code', u'Data Sender GPS Coordinates'), ('form_model_id_q1', 'text'), ('form_model_id_q2', 'integer'),
            ('form_model_id_q3_details.code1', 'label1'), ('form_model_id_q3_details.code2', 'label2')])

        result = SubmissionAnalysisHeader(self.form_model).get_header_dict()

        self.assertDictEqual(expected, result)

    def test_get_header_dict_from_form_model_with_single_unique_id_question_inside_repeat(self):
        self.form_model.fields = [self.field1, self.field2, self.repeat_field]
        self.form_model.entity_questions = [self.field4]
        expected = {'date': 'Submission Date', 'ds_id': 'Data Sender Id', 'ds_name': 'Data Sender Name',
                    'form_model_id_q1': 'Enter Text',
                    'form_model_id_q2': 'Enter a Number',  'form_model_id_repeat-q1': 'Enter Text',
                    'form_model_id_repeat-q4': 'Which school are you reporting on'}
        result = AllSubmissionHeader(self.form_model).get_header_dict()
        self.assertDictEqual(expected, result)

    def test_should_return_submission_log_specific_header_fields(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]
        self.form_model.is_poll = False
        headers = AllSubmissionHeader(self.form_model).get_header_field_names()

        expected = ["ds_id", "ds_name", "date", "status", "form_model_id_q1", "form_model_id_q2", "form_model_id_q3", "form_model_id_q3_unique_code", "form_model_id_q4", "form_model_id_q4_unique_code"]
        self.assertListEqual(expected, headers)

    def test_should_return_submission_log_specific_header_fields_for_poll(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]
        self.form_model.is_poll = True
        headers = AllSubmissionHeader(self.form_model).get_header_field_names()

        expected = ["ds_id", "ds_name", "date", "form_model_id_q1", "form_model_id_q2", "form_model_id_q3", "form_model_id_q3_unique_code", "form_model_id_q4", "form_model_id_q4_unique_code"]
        self.assertListEqual(expected, headers)


    def test_submission_status_headers_for_success_submissions(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]

        headers = SuccessSubmissionHeader(self.form_model).get_header_field_names()

        expected = ["ds_id", "ds_name", "date", "form_model_id_q1", "form_model_id_q2", "form_model_id_q3", "form_model_id_q3_unique_code", "form_model_id_q4", "form_model_id_q4_unique_code"]
        self.assertListEqual(expected, headers)

    def test_submission_status_headers_for_errored_submissions(self):
        self.form_model.fields = [self.field1, self.field2, self.field3, self.field4]
        self.form_model.entity_questions = [self.field3, self.field4]

        headers = ErroredSubmissionHeader(self.form_model).get_header_field_names()

        expected = ["ds_id", "ds_name", "date","error_msg", "form_model_id_q1", "form_model_id_q2", "form_model_id_q3", "form_model_id_q3_unique_code", "form_model_id_q4", "form_model_id_q4_unique_code"]

        self.assertListEqual(expected, headers)


    def test_get_header_dict_from_form_model_with_group_field(self):
        self.get_entity_type_info_mock.return_value = dict(entity='clinic', code='cli002', names=['name1', 'name2'],
                                                          codes=['code1', 'code2'], labels=['label1','label2'], data=[])
        self.form_model.fields = [self.repeat_field]
        self.form_model._dbm = Mock(spec=FormModel)
        
        expected = OrderedDict([('date', u'Submission Date'), ('datasender.id', u'Data Sender Id'),
            ('datasender.name', u'Data Sender Name'), ('datasender.mobile_number', u'Data Sender Mobile Number'),
            ('datasender.email', u'Data Sender Email'), ('datasender.location', u'Data Sender Location'),
            ('datasender.geo_code', u'Data Sender GPS Coordinates'), ('form_model_id_repeat-q1', 'text'),
            ('form_model_idrepeat-q4_details.code1', 'label1'), ('form_model_idrepeat-q4_details.code2', 'label2')])

        result = SubmissionAnalysisHeader(self.form_model).get_header_dict()

        self.assertDictEqual(expected, result)


class TestHeaderFactory(unittest.TestCase):
    def test_should_return_header_instance_based_on_submission_type(self):
        form_model = Mock(spec=FormModel)
        self.assertIsInstance(HeaderFactory(form_model).create_header("all"), AllSubmissionHeader)
        self.assertIsInstance(HeaderFactory(form_model).create_header("success"), SuccessSubmissionHeader)
        self.assertIsInstance(HeaderFactory(form_model).create_header("error"), ErroredSubmissionHeader)
        self.assertIsInstance(HeaderFactory(form_model).create_header("analysis"), SubmissionAnalysisHeader)