import unittest
from django.test import Client, TestCase
from datawinners.accountmanagement.models import Organization
from datawinners.sms.models import SMS


class TestSMSReceipt(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.client = Client()
        o = Organization.objects.get(org_id='SLX364903')
        SMS(message_id="1234", organization=o, message="abc", status="Submitted").save()

    def test_sms_receipt(self):
        param = {u'transport_status': u'ACCEPTD', u'delivered_at': u'2014-01-15 12:04:07.000000',
                 u'transport_name': u'smppclient1', u'created_at': u'2014-01-15 07:16:30.459599',
                 u'updated_at': u'2014-01-15 07:18:26.599290', u'callback_name': u'sms_receipt',
                 u'from_msisdn': u'1234123413',
                 u'to_msisdn': u'919880734937', u'message': u'No organization found for telephone number 1234123413',
                 u'id': u'1234'}
        resp = self.client.post('/receipt', param)
        sms = SMS.objects.get(message_id="1234")
        self.assertEquals("", resp.content)
        self.assertEquals("ACCEPTD",sms.status)
        self.assertEquals("smppclient1",sms.smsc)

    def tearDown(self):
        SMS.objects.get(message_id="1234").delete()