import os
import tempfile
from django.test import TestCase, Client
import xlrd


class TestSubmissionImport(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def test_import_template(self):
        resp = self.client.get('/entity/subject/template/cli051/?filename=clinic%20test%20project')
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        sheet = workbook.sheet_by_index(0)
        self.assertEqual(
            [
                u"entity_question\n Enter unique ID\n\n ",
                u"Name\n Answer must be a word 10 characters maximum\n\n ",
                u"Father age\n Answer must be a number between 18-100.\n\n ",
                u"Report date\n Answer must be a date in the following format: day.month.year\n\n Example: 25.12.2011",
                u"Blood Group\n Enter 1 answer from the list.\n\n Example: a",
                u"Symptoms\n Enter 1 or more answers from the list.\n\n Example: a or ab",
                u"What is the GPS code for clinic?\n Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy.\n\n Example: -18.1324,27.6547",
                u"Required Medicines\n Enter 1 or more answers from the list.\n\n Example: a or ab",
            ], sheet.row_values(0, 0, 8))