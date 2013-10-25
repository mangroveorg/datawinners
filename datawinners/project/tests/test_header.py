# encoding=utf-8
from unittest import TestCase
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from mangrove.utils.json_codecs import encode_json
from datawinners.project.Header import Header, SubmissionsPageHeader
from datawinners.project.tests.form_model_generator import FormModelGenerator


class TestHeader(TestCase):
    def setUp(self):
        super(TestHeader, self).setUp()
        self.form_model_generator = FormModelGenerator(Mock(spec=DatabaseManager))

    def test_should_return_header_info_dict(self):
        expected_header_list = (
        "Submission Id", "Clinic", "Reporting Period", "Submission Date", "Data Sender", "Zhat are symptoms?",
        "What is your blood group?")
        expected_header_name_list = repr(encode_json((
        "Submission Id", "Clinic", "Reporting Period", "Submission Date", "Data Sender", "Zhat are symptoms?",
        "What is your blood group?")))
        expected_header_type_list = repr(encode_json(('', "", 'dd.mm.yyyy', 'dd.mm.yyyy', "", "", "")))
        expected_header_info_dict = {'header_list': expected_header_list, 'header_name_list': expected_header_name_list,
                                     'header_type_list': expected_header_type_list}

        header_info = Header(form_model=self.form_model_generator.form_model()).info

        self.assertEqual(3, len(header_info))
        self.assertDictEqual(expected_header_info_dict, header_info)

    def test_should_create_header_list_with_data_sender_if_the_project_is_not_a_summary_project(self):
        form_model = self.form_model_generator.form_model()
        expected_header_list = (
        "Submission Id", "Clinic", "Reporting Period", "Submission Date", "Data Sender", "Zhat are symptoms?",
        "What is your blood group?")
        expected_header_type_list = ('', "", 'dd.mm.yyyy', 'dd.mm.yyyy', "", "", "")

        self.assertEqual(expected_header_list, Header(form_model).header_list)
        self.assertEqual(expected_header_type_list, Header(form_model).header_type_list)

    def test_should_create_header_list_without_reporter_column_if_the_project_is_a_summary_project(self):
        form_model = self.form_model_generator.summary_form_model_without_rp()

        expected_header_list = (
        "Submission Id", "Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?")
        expected_header_type_list = ('', 'dd.mm.yyyy', '', '', '')

        self.assertEqual(expected_header_list, Header(form_model).header_list)
        self.assertEqual(expected_header_type_list, Header(form_model).header_type_list)

    def test_should_create_header_list_without_reporter_column_if_the_project_is_a_summary_project(self):
        form_model = self.form_model_generator.summary_form_model_without_rp()

        expected_header_list = (
        "Submission Id", "Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?")
        expected_header_type_list = ('', 'dd.mm.yyyy', '', '', '')

        self.assertEqual(expected_header_list, Header(form_model).header_list)
        self.assertEqual(expected_header_type_list, Header(form_model).header_type_list)

    def test_should_create_header_list_with_gps_type(self):
        form_model = self.form_model_generator.form_model_with_gps_question()

        expected_header_list = ("Submission Id", "Clinic", "Submission Date", "Data Sender", "Where do you stay?")
        expected_header_type_list = ('', '', 'dd.mm.yyyy', "", "gps")

        self.assertEqual(expected_header_list, Header(form_model).header_list)
        self.assertEqual(expected_header_type_list, Header(form_model).header_type_list)


class AllSubmissionsHeaderTest(TestCase):
    def setUp(self):
        super(AllSubmissionsHeaderTest, self).setUp()
        self.form_model_generator = FormModelGenerator(Mock(spec=DatabaseManager))
        self.form_model = self.form_model_generator.form_model()



    def test_should_contain_column_headers_for_success_submissions(self):
        expected_header_list_for_success_submissions = (
        "Submission Id", "Data Sender", "Submission Date", "Clinic", "Reporting Period",
        "Zhat are symptoms?", "What is your blood group?")
        self.assertEquals(expected_header_list_for_success_submissions,SubmissionsPageHeader(self.form_model,'success').header_list)

    def test_should_contain_column_headers_for_erred_submissions(self):

        expected_header_list_for_erred_submissions = (
        "Submission Id", "Data Sender", "Submission Date","Error Messages", "Clinic", "Reporting Period",
        "Zhat are symptoms?", "What is your blood group?")
        self.assertEquals(expected_header_list_for_erred_submissions,SubmissionsPageHeader(self.form_model,'error').header_list)

    def test_should_contain_column_headers_for_all_submissions(self):
        expected_header_list_for_all_submissions = (
        "Submission Id", "Data Sender", "Submission Date","Status", "Clinic", "Reporting Period",
        "Zhat are symptoms?", "What is your blood group?")
        self.assertEquals(expected_header_list_for_all_submissions,SubmissionsPageHeader(self.form_model,'all').header_list)

        expected_header_type_list = ('', '', 'dd.mm.yyyy', '', '', '', 'dd.mm.yyyy', '', '')

        #self.assertEqual(expected_header_type_list, SubmissionsPageHeader(self.form_model,'all').header_type_list)



