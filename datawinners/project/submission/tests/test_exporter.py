# from unittest import TestCase
# from django.contrib.auth.models import User
# from django.http import HttpResponse
# from mock import Mock
# from datawinners.project.submission.exporter import SubmissionExporter
# from mangrove.form_model.form_model import FormModel
#
#
# # class ExporterTest(TestCase):
# #
# #     def test_export(self):
# #         with
# #         form_model = Mock(FormModel)
# #         project_name = "a"
# #         user = Mock(User)
# #         exporter = SubmissionExporter(form_model, project_name, user)
# #         response = exporter.create_excel_response(type, 'search_text')
# #         self.assertTrue(isinstance(response, HttpResponse))
# #         self.assertEquals(response.content_type, "application/vnd.ms-excel")
import os
import tempfile
from django.test import TestCase, Client
import xlrd


class ExporterTest(TestCase):
    def test_export(self):
        self.client = Client()
        self.client.login(username='tester150411@gmail.com', password='tester150411')
        resp = self.client.post('/project/export/log', {'project_name': 'test data sorting', 'type':'all', 'search':'', 'questionnaire_code':'cli018'})
        print resp
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        print "file is %s" % xlfile_name
        sheet = workbook.sheet_by_index(0)
        self.assertEqual([u'Datasender Name', u'Datasender Id', u'Submission Date', u'Status', u'Clinic'], sheet.row_values(0,0,5))



