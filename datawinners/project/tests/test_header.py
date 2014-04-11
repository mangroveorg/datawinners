# encoding=utf-8
from unittest import TestCase
from mock import Mock, patch, MagicMock
from datawinners.search.submission_headers import HeaderFactory, AllSubmissionHeader
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.field import UniqueIdField
from mangrove.form_model.form_model import FormModel
from mangrove.utils.json_codecs import encode_json
from datawinners.project.Header import Header, SubmissionsPageHeader
from datawinners.project.tests.form_model_generator import FormModelGenerator


class TestHeader(TestCase):
    def setUp(self):
        super(TestHeader, self).setUp()
        self.form_model_generator = FormModelGenerator(Mock(spec=DatabaseManager))

    def test_should_return_header_info_dict(self):
        expected_header_list = (
            "Submission Id", "Clinic", "Submission Date", "Data Sender","Report date", "Zhat are symptoms?",
            "What is your blood group?")
        expected_header_name_list = repr(encode_json((
            "Submission Id", "Clinic",  "Submission Date", "Data Sender", "Report date","Zhat are symptoms?",
            "What is your blood group?")))
        expected_header_type_list = repr(encode_json(('', "", 'dd.mm.yyyy', "", 'dd.mm.yyyy', "", "")))
        expected_header_info_dict = {'header_list': expected_header_list, 'header_name_list': expected_header_name_list,
                                     'header_type_list': expected_header_type_list}

        header_info = Header(form_model=self.form_model_generator.form_model()).info

        self.assertEqual(3, len(header_info))
        self.assertDictEqual(expected_header_info_dict, header_info)

    def test_should_create_header_list_with_data_sender_if_the_project_is_not_a_summary_project(self):
        form_model = self.form_model_generator.form_model()
        expected_header_list = (
            "Submission Id", "Clinic", "Submission Date", "Data Sender","Report date",  "Zhat are symptoms?",
            "What is your blood group?")
        expected_header_type_list = ('', "", 'dd.mm.yyyy',"", 'dd.mm.yyyy',  "", "")

        self.assertEqual(expected_header_list, Header(form_model).header_list)
        self.assertEqual(expected_header_type_list, Header(form_model).header_type_list)


    def test_should_create_header_list_with_gps_type(self):
        form_model = self.form_model_generator.form_model_with_gps_question()

        expected_header_list = ("Submission Id", "Clinic", "Submission Date", "Data Sender", "Where do you stay?")
        expected_header_type_list = ('', '', 'dd.mm.yyyy', "", "gps")

        self.assertEqual(expected_header_list, Header(form_model).header_list)
        self.assertEqual(expected_header_type_list, Header(form_model).header_type_list)


class TestSubmissionsPageHeader(TestCase):
    def test_remove_meta_fields_from_header(self):
        form_model = MagicMock(spec=FormModel, id='form_id')
        form_model.entity_questions = [UniqueIdField('clinic', 'name', 'q1', 'which clinic')]

        with patch.object(HeaderFactory, 'create_header') as create_header:
            all_submission_header = Mock(spec=AllSubmissionHeader)
            create_header.return_value = all_submission_header
            all_submission_header.get_header_field_dict.return_value = {'ds_name': 'tester', 'ds_id': 'rep1',
                                                                        'form_id_q1': 'which clinic',
                                                                        'form_id_q1_unique_code': 'cli001',
                                                                        'form_id_q2': 'Age?'}
            headers = SubmissionsPageHeader(form_model, 'all').get_column_title()

            self.assertListEqual(['tester', 'which clinic', 'Age?'], headers)

