import os
import tempfile
from django.test import TestCase, Client
import xlrd


class TestExporter(TestCase):
    def setUp(self):
        self.client = Client()
        self.create_submissions()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def test_export(self):
        resp = self.client.post('/project/export/log',
                                {'project_name': 'test data sorting', 'type': 'all', 'search': 'export18',
                                 'questionnaire_code': 'cli001'})
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        print "file is %s" % xlfile_name
        sheet = workbook.sheet_by_index(0)
        self.assertEqual([u'Datasender Name', u'Datasender Id', u'Submission Date', u'Status', u'Clinic'],
                         sheet.row_values(0, 0, 5))
        self.assertEqual([u'export18'], sheet.row_values(1, 7, 8))

    def create_submissions(self):
        _from = "917798987116"
        _to = "919880734937"
        for i in [17, 18]:
            message = "cli001 cid001 export%s %d 02.02.2012 a a 2,2 a" % (i, i)
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
            self.client.post("/submission", data)


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



