from django.test import TestCase
from datawinners.project.submission.exporter import SubmissionExporter
from datawinners.project.submission.formatter import SubmissionFormatter
from mangrove.form_model.field import ExcelDate
from mock import Mock, patch
from datawinners.project.submission.export import export_to_new_excel
from django.http import HttpResponse
import datetime, StringIO
from openpyxl import load_workbook

class TestSubmissionExporter(TestCase):
    def setUp(self):
        self.format_row_mock = patch.object(SubmissionFormatter, "format_row")
        self.format_row_patch = self.format_row_mock.start()
        date_1 = ExcelDate(datetime.datetime(2012, 04, 24), 'mm.yyyy')
        self.data = data = [{'_source':[u'N/A', '', date_1, u'Success', u'Analalava', u'cli8', u'Kanda (",)', 34.0,
                 date_1, u'B+', u'Dry cough; Neurological disorders ', 38.3452, 15.3345, u'R\xe9trovir']}]
        self.headers = [u'Data Sender', u'Datasender Id', u'Submission Date', u'Status', u'What is associat\xe9d entity?',
                   u'clinic ID', u'What is your nam\xe9?', u'What is age \xf6f father?', u'What is r\xe9porting date?',
                   u'What is your blood group?', u'What ar\xe9 symptoms?', u'What is the GPS code for clinic? Latitude',
                   u'What is the GPS code for clinic? Longitude', u'What are the required medicines?']

    def tearDown(self):
        self.format_row_mock.stop()


    def test_should_export_data_in_xlsx(self):
        self.format_row_patch.side_effect = lambda x: x
        file_response = export_to_new_excel(self.headers, self.data, 'filename', SubmissionFormatter(self.headers, None))
        self.assertTrue(isinstance(file_response, HttpResponse))
        self.assertEquals(file_response.get('Content-Disposition', None), "attachment; filename=filename.xlsx")

        f = StringIO.StringIO(file_response.content)
        wb = load_workbook(f)
        ws = wb.get_active_sheet()
        self.assertEqual(len(ws.rows), 2)
        self.assertEqual(len(ws.columns), 14)
        f.close()