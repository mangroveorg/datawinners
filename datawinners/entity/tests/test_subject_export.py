import os
import random
import tempfile
import uuid
from django.test import TestCase, Client
import xlrd


class TestSubjectExport(TestCase):
    def setUp(self):
        self.client = Client()
        self.mobile_number = self.random_number(6)
        self.create_subject()
        self.client.login(username='tester150411@gmail.com', password='tester150411')

    def random_number(self, length):
        return ''.join(random.sample('1234567890', length))

    def test_export(self):
        resp = self.client.post('/entity/subject/export/',
                                {'subject_type': 'clinic', 'query_text': self.mobile_number})
        xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
        os.write(xlfile_fd, resp.content)
        os.close(xlfile_fd)
        workbook = xlrd.open_workbook(xlfile_name)
        print "file is %s" % xlfile_name
        sheet = workbook.sheet_by_index(0)
        self.assertEqual(
            [u"What is the clinic's first name?\nAnswer must be a word\n\n",
             u"What is the clinic's last name?\nAnswer must be a word\n\n",
             u"What is the clinic's location?\nEnter name of the location.\n\nExample: Nairobi",
             u"What is the clinic's GPS co-ordinates?\nAnswer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy.\n\nExample: -18.1324,27.6547",
             u"What is the clinic's mobile telephone number?\nAnswer must be country code plus telephone number\n\nExample: 261333745269"],
            sheet.row_values(0, 0, 5))
        self.assertEqual([u'firstname', u'lastname', u'location', u'3.0, 3.0', self.mobile_number],
                         sheet.row_values(1, 0, 5))
        self.assertEqual([], sheet.row_values(1, 6))

    def create_subject(self):
        _from = "917798987116"
        _to = "919880734937"

        message = "cli firstname lastname location 3,3 %s" % self.mobile_number
        data = {"message": message, "from_msisdn": _from, "to_msisdn": _to, "message_id": uuid.uuid1().hex}
        self.client.post("/submission", data)
