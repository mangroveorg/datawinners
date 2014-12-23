# coding=utf-8
import os
import tempfile
import unittest
import uuid

from django.test import Client
from nose.plugins.attrib import attr
import xlrd


@attr('functional_test')
class TestExporter(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.create_submissions()
        self.client.login(username='tester150411@gmail.com', password='tester150411')


    def test_export(self):
        resp = self.client.post('/project/export/log?type=all',
                                {'project_name': 'test-data-sorting',
                                 'search_filters': "{\"search_text\":\"export18\",\"dateQuestionFilters\":{}}",
                                 'questionnaire_code': 'cli001'})
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        print "file is %s" % xlfile_name
        sheet = workbook.sheet_by_index(0)
        self.assertEqual([u'Data Sender', u'Datasender Id', u'Submission Date', u'Status', u'What is associat\xe9d entity?', u'clinic ID',
                          u"What is your namé?", u"What is age öf father?",u'What is réporting date?',
                          u"What is your blood group?", u"What aré symptoms?",
                          u'What is the GPS code for clinic? Latitude', u'What is the GPS code for clinic? Longitude',
                          u'What are the required medicines?'], sheet.row_values(0, 0, 14))
        self.assertEqual([2.0, 2.0], sheet.row_values(1, 11, 13))

        self.assertEqual([u'export18'], sheet.row_values(1, 6,7))

    def create_submissions(self):
        _from = "917798987116"
        _to = "919880734937"
        for i in [17, 18]:
            message = "cli001 cid001 export%s %d 02.02.2012 a a 2,2 a" % (i, i)
            data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id": uuid.uuid1().hex}
            self.client.post("/submission", data)



