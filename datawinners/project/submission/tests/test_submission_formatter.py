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
        self.assertEquals(values, [['3', '3']])

    def test_should_split_gps_values_based_on_space(self):
        columns = {'form_id_q1': {'type': 'geocode', 'label':'what is gps'}}
        submission_list = [{'form_id_q1': '3.90     -7.89'}]

        headers, values = SubmissionFormatter(columns).format_tabular_data(submission_list)

        self.assertEquals(headers, ['what is gps Latitude', 'what is gps Longitude'])
        self.assertEquals(values, [['3.90', '-7.89']])

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