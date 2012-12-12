# encoding=utf-8
from unittest import TestCase
from mock import Mock
from mangrove.datastore.database import DatabaseManager
from project.Header import Header, AllSubmissionsHeader
from project.tests.form_model_generator import FormModelGenerator

class TestHeader(TestCase):
    def setUp(self):
        super(TestHeader, self).setUp()
        self.form_model_generator = FormModelGenerator(Mock(spec=DatabaseManager))

    def test_should_create_header_list_with_data_sender_if_the_project_is_not_a_summary_project(self):
        form_model = self.form_model_generator.form_model()
        expected_header = (["Clinic", "Reporting Period", "Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?"],
                           ["", 'dd.mm.yyyy', 'dd.mm.yyyy', "", "", ""])

        self.assertEqual(expected_header, (Header(form_model)).get())

    def test_should_create_header_list_without_reporter_column_if_the_project_is_a_summary_project(self):
        form_model = self.form_model_generator.summary_form_model_without_rp()
        expected_header = (["Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?"],
                           ['dd.mm.yyyy', '', '', ''])

        self.assertEqual(expected_header, Header(form_model).get())

    def test_should_create_header_list_without_reporter_column_if_the_project_is_a_summary_project(self):
        form_model = self.form_model_generator.summary_form_model_without_rp()

        expected_header = (["Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?"],
                           ['dd.mm.yyyy', '', '', ''])
        self.assertEqual(expected_header, Header(form_model).get())

    def test_should_create_header_list_with_gps_type(self):
        form_model = self.form_model_generator.form_model_with_gps_question()

        expected_header = (["Clinic", "Submission Date", "Data Sender", "Where do you stay?"],
                           ['','dd.mm.yyyy', "", "gps"])
        self.assertEqual(expected_header, Header(form_model).get())


class AllSubmissionsHeaderTest(TestCase):
    def setUp(self):
        super(AllSubmissionsHeaderTest, self).setUp()
        self.form_model_generator = FormModelGenerator(Mock(spec=DatabaseManager))

    def test_should_contain_column_status_for_all_submissions_head(self):
        form_model = self.form_model_generator.form_model()
        expected_header = (["Clinic", "Reporting Period", "Submission Date", "Status", "Data Sender", "Zhat are symptoms?", "What is your blood group?"],
                           ["", 'dd.mm.yyyy', 'dd.mm.yyyy', "", "", ""])

        self.assertEqual(expected_header, (AllSubmissionsHeader(form_model)).get())