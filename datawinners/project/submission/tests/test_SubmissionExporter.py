from django.test import TestCase
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.formatter import SubmissionFormatter
from mangrove.form_model.field import ExcelDate
from mock import Mock, patch
from datawinners.project.submission.export import export_to_new_excel
from django.http import HttpResponse
import datetime
import StringIO
from openpyxl import load_workbook
from collections import OrderedDict


class TestSubmissionExporter(TestCase):

    def setUp(self):
        date_1 = ExcelDate(datetime.datetime(2012, 04, 24), 'mm.yyyy')
        columns = OrderedDict()
        columns['date'] = {'label': u'Submission Date'}
        columns['datasender.id'] = {
            'type': 'short_code', 'label': u'Data Sender Id'}
        columns['datasender.name'] = {
            'type': 'text', 'label': u'Data Sender Name'}
        columns['datasender.mobile_number'] = {
            'type': 'telephone_number', 'label': u'Data Sender Mobile Number'}
        columns['datasender.email'] = {
            'type': 'email', 'label': u'Data Sender Email'}
        columns['datasender.location'] = {
            'type': 'text', 'label': u'Data Sender Location'}
        columns['datasender.geo_code'] = {
            'type': 'geocode', 'label': u'Data Sender GPS Coordinates'}
        columns['348e50c0c78711e58c3b60f81dc5021a_q2_details.q1'] = {
            'type': 'text', 'label': "What is the city's first name?"}
        columns['348e50c0c78711e58c3b60f81dc5021a_q2_details.q2'] = {
            'type': 'text', 'label': "What is the city's last name?"}
        columns['348e50c0c78711e58c3b60f81dc5021a_q2_details.q3'] = {
            'type': 'list', 'label': "What is the city's location?"}
        columns['348e50c0c78711e58c3b60f81dc5021a_q2_details.q4'] = {
            'type': 'geocode', 'label': "What is the city's GPS co-ordinates?"}
        columns['348e50c0c78711e58c3b60f81dc5021a_q2_details.q5'] = {
            'type': 'telephone_number', 'label': "What is the city's mobile telephone number?"}
        columns['348e50c0c78711e58c3b60f81dc5021a_q2_details.q6'] = {
            'type': 'short_code', 'label': "What is the city's Unique ID Number?"}
        columns['348e50c0c78711e58c3b60f81dc5021a_q3'] = {
            'type': 'integer', 'label': 'Total sales'}

        self.columns = columns

        record = {
            u'_score': 0.0, u'_type': u'348e50c0c78711e58c3b60f81dc5021a',
            u'_id': u'49339cabc78811e58fd660f81dc5021a',
            u'_source': {u'status': u'Success',
                         u'datasender': {
                             u'geo_code': [],
                             u'name': u'Einstein', u'email': u'Einsteink@mailinator.com', u'location': [u'India'],
                             u'mobile_number': u'1345555', u'id': u'rep2'
                         },
                         u'is_anonymous': False, u'348e50c0c78711e58c3b60f81dc5021a_q3': u'5000.0',
                         u'348e50c0c78711e58c3b60f81dc5021a_q2': u'chennai',
                         u'348e50c0c78711e58c3b60f81dc5021a_q2_details': {
                             u'q1': u'madras',
                             u'q3': [u'south', u'India'],
                             u'q2': u'chennai', u'q5': u'96766888', u'q4': [-18.0, 33.0], u'q6': u'cit1'
                         }, u'ds_id': u'rep2', u'error_msg': u'', u'ds_name': u'Einstein', u'media': {}, u'date': u'Jan. 30, 2016, 07:33 PM',
                         u'348e50c0c78711e58c3b60f81dc5021a_q2_unique_code': u'cit1', u'void': False
                         }, u'_index': u'hni_puretalent_ske175197'
        }
        self.data = [record]

        preferences = [
            {'data': 'date', 'visibility': True, 'title': u'Submission Date'},
            {'data': 'datasender',
             'children': [
                 {'data': 'datasender.name', 'visibility': True,
                  'title': u'Data Sender Name'},
                 {'data': 'datasender.id', 'visibility': True,
                  'title': u'Data Sender Id'},
                 {'data': 'datasender.mobile_number', 'visibility': False,
                  'title': u'Data Sender Mobile Number'},
                 {'data': 'datasender.email', 'visibility': False,
                  'title': u'Data Sender Email'},
                 {'data': 'datasender.location', 'visibility': False,
                  'title': u'Data Sender Location'},
                 {'data': 'datasender.geo_code', 'visibility': False, 'title': u'Data Sender GPS Coordinates'}],
             'visibility': False, 'title': u'Data Sender'
             },
            {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details',
             'children': [
                 {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details.q1',
                  'visibility': False, 'title': "What is the city's first name?"},
                 {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details.q2', 'visibility': True,
                  'title': "What is the city's last name?"},
                 {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details.q3', 'visibility': False,
                  'title': "What is the city's location?"},
                 {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details.q4', 'visibility': False,
                  'title': "What is the city's GPS co-ordinates?"},
                 {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details.q5', 'visibility': False,
                  'title': "What is the city's mobile telephone number?"},
                 {'data': '348e50c0c78711e58c3b60f81dc5021a_q2_details.q6', 'visibility': True,
                  'title': "What is the city's Unique ID Number?"}
             ], 'visibility': False, 'title': 'City'},
            {'data': '348e50c0c78711e58c3b60f81dc5021a_q3', 'visibility': True, 'title': 'Total sales'}]
        self.preferences = preferences

    def test_should_export_data_in_xlsx(self):
        local_time_delta = '+', 0, 0
        submission_formatter = SubmissionFormatter(
            self.columns, local_time_delta, self.preferences)
        header_list = submission_formatter.format_header_data()
        file_response = export_to_new_excel(header_list, self.data, 'filename', submission_formatter
                                            )
        self.assertTrue(isinstance(file_response, HttpResponse))
        self.assertEquals(file_response.get(
            'Content-Disposition', None), "attachment; filename=filename.xlsx")

        f = StringIO.StringIO(file_response.content)
        wb = load_workbook(f)
        ws = wb.get_active_sheet()
        row_values = [[cell.value for cell in row] for row in ws.rows]
        expected_row_values = [
            [
                u'Submission Date',
                u'Data Sender Name',
                u'Data Sender Id',
                u"What is the city's last name?",
                u"What is the city's Unique ID Number?",
                u'Total sales'
            ],
            [
                datetime.datetime(
                    2016, 1, 30, 19, 32, 59, 999997), u'Einstein', u'rep2', u'chennai', u'cit1', 5000
            ]
        ]

        column_values = [[cell.value for cell in column]
                         for column in ws.columns]
        expected_column_values = [
            [
                u'Submission Date',
                datetime.datetime(
                    2016, 1, 30, 19, 32, 59, 999997)
            ],
            [
                u'Data Sender Name',
                u'Einstein'
            ],
            [
                u'Data Sender Id',
                u'rep2'
            ],
            [
                u"What is the city's last name?",
                u'chennai'
            ],
            [
                u"What is the city's Unique ID Number?",
                u'cit1'
            ],
            [
                u'Total sales',
                5000
            ]
        ]
        self.assertEqual(len(ws.rows), 2)
        self.assertEqual(len(ws.columns), 6)
        self.assertEqual(row_values, expected_row_values)
        self.assertEqual(column_values, expected_column_values)
        f.close()
