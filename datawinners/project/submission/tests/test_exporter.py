import os
import tempfile
from django.test import TestCase, Client
import xlrd


class ExporterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.create_submissions()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def test_export(self):
        resp = self.client.post('/project/export/log', {'project_name': 'test data sorting', 'type':'all', 'search':'export20', 'questionnaire_code':'cli001'})
        print resp
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        print "file is %s" % xlfile_name
        sheet = workbook.sheet_by_index(0)
        self.assertEqual([u'Datasender Name', u'Datasender Id', u'Submission Date', u'Status', u'Clinic'], sheet.row_values(0,0,5))
        self.assertEqual([u'export20' ], sheet.row_values(1,7,8))

    def create_submissions(self):
        _from = "917798987116"
        _to = "919880734937"
        for i in [18,19]:
            message = "cli001 cid001 export%s %d 02.02.2012 a a 2,2 a" % (i,i)
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to}
            self.client.post("/submission", data)



