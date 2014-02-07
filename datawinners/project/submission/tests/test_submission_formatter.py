from unittest import TestCase
import datetime
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from datawinners.project.submission.formatter import SubmissionFormatter
from mangrove.form_model.field import ExcelDate


class TestSubmissionFormatter(TestCase):
    def test_should_split_gps_values_and_append_latitude_and_longitude_in_headers(self):
        columns = {'form_id_q1': {'type': 'geocode', 'label':'what is gps'}}
        submission_list = [{'form_id_q1': '  3  ,  3'}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is gps Latitude', 'what is gps Longitude'])
        self.assertEquals(values, [[3.0, 3.0]])

    def test_should_split_gps_values_based_on_space(self):
        columns = {'form_id_q1': {'type': 'geocode', 'label':'what is gps'}}
        submission_list = [{'form_id_q1': '3.90     -7.89'}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is gps Latitude', 'what is gps Longitude'])
        self.assertEquals(values, [[3.9, -7.89]])

    def test_should_retain_junk_values_as_is_though_type_is_geo_coordinate(self):
        columns = {'form_id_q1': {'type': 'geocode', 'label':'what is gps'}}
        submission_list = [{'form_id_q1': 'aa'}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is gps Latitude', 'what is gps Longitude'])
        self.assertEquals(values, [['aa', '']])


    def test_should_give_back_empty_values_and_append_latitude_and_longitude_in_headers_when_no_gps_value_in_submission(self):
        columns = {'form_id_q1': {'type': 'geocode', 'label':'what is gps'}, 'form_id_q2':{'type': 'text', 'label': 'say hi'}}
        submission_list = [{'form_id_q2': 'hello'}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is gps Latitude', 'what is gps Longitude', 'say hi'])
        self.assertEquals(values, [['', '', 'hello']])

    def test_should_give_back_values_and_headers_for_all_fields_except_date_and_gps(self):
        columns = {'form_id_q1': {'type': 'text', 'label':'what is name'}}
        submission_list = [{'form_id_q1': 'name'}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is name'])
        self.assertEquals(values, [['name']])

    def test_should_give_back_excel_date_field_for_date_type_question(self):
        columns = {'form_id_q1': {'type': 'date', 'label':'what is date', 'format': 'dd.mm.yyyy'}}
        date_1 = '09.12.2013'
        submission_list = [{'form_id_q1': date_1}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is date'])
        result_date = datetime.datetime.strptime(date_1, '%d.%m.%Y')
        self.assertEquals(values, [[ExcelDate(result_date, 'dd.mm.yyyy')]])

    def test_should_give_back_string_for_invalid_date(self):
        columns = {'form_id_q1': {'type': 'date', 'label':'what is date', 'format': 'dd.mm.yyyy'}}
        date_1 = '12.2013'
        submission_list = [{'form_id_q1': date_1}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is date'])
        self.assertEquals(values, [[date_1]])

    def test_should_give_back_excel_date_field_for_submission_date_type_question(self):
        columns = {'form_id_q1': {'type': 'date', 'label':'what is submission date', 'format': "submission_date"}}
        date_1 = 'Dec. 09, 2013, 10:48 AM'
        submission_list = [{'form_id_q1': date_1}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is submission date'])
        result_date = datetime.datetime.strptime(date_1, SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
        self.assertEquals(values, [[ExcelDate(result_date, "submission_date")]])

    def test_should_return_empty_when_date_value_is_invalid(self):
        columns = {'form_id_q2': {'type': 'date', 'label':'what is submission date', 'format': "submission_date"}}
        date_1 = 'Dec. 09, 2013, 10:48 AM'
        submission_list = [{'form_id_q1': date_1}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is submission date'])
        self.assertEquals(values, [['']])

    def test_should_concatenate_multi_select_values(self):
        columns = {'form_id_q1': {'type': 'select', 'label':'What programming languages do you use'}}
        submission_list = [{'form_id_q1': ["Python", "C#", "Java"]}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['What programming languages do you use'])
        self.assertEquals(values, [['Python, C#, Java']])

    def test_should_parse_numeric_values_when_type_is_numeric(self):
        columns = {'form_id_q1': {'type': 'integer', 'label':'How many hours do you code'}}
        submission_list = [{'form_id_q1': "12.0"}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['How many hours do you code'])
        self.assertEquals(values, [[12.0]])

    def test_should_treat_no_numeric_answers_as_text_even_when_though_type_is_numeric(self):
        columns = {'form_id_q1': {'type': 'integer', 'label':'How many hours do you code'}}
        submission_list = [{'form_id_q1': "some rubbish"}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['How many hours do you code'])
        self.assertEquals(values, [["some rubbish"]])

    def test_should_return_empty_value_for_multi_select_field_when_no_answer_present(self):
        columns = {'form_id_q1': {'type': 'select', 'label':'Where do you code from'}}
        submission_list = [{}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['Where do you code from'])
        self.assertEquals(values, [[""]])

