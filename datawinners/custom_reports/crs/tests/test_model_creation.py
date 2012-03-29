import unittest
from datetime import datetime
from collections import OrderedDict
from datawinners.custom_reports.crs.handler import CRSCustomReportHandler, model_routing_dict
from datawinners.custom_reports.crs.models import WayBillSent, WayBillReceived

class TestWayBillSent(unittest.TestCase):
    def setUp(self):
        self.way_bill_sent = None
        self.question_code = 'WBS01'
        model_routing_dict[self.question_code]=WayBillSent

    def tearDown(self):
        if self.way_bill_sent is not None:
            self.way_bill_sent.delete()

    def test_should_create_WayBillSent_from_submission_data(self):
        sent_date = datetime.strptime('11.11.2011', '%d.%m.%Y')
        waybill_sent_submission_data = OrderedDict(
            [('q1', u'pac1'), ('q2', u'2'), ('q3', sent_date), ('q4', u'Transfer'), ('q5', u'2'),
                ('q6', u'test'), ('q7', u'9'), ('q8', u'Oil'), ('q9', 400)])
        crs_custom_report_handler = CRSCustomReportHandler()
        crs_custom_report_handler.handle(self.question_code, waybill_sent_submission_data)
        self.way_bill_sent = WayBillSent.objects.filter(q1='pac1')[0]
        self.assertEquals('2', self.way_bill_sent.q2)
        self.assertEquals(datetime.date(sent_date), self.way_bill_sent.q3)
        self.assertEquals('Transfer', self.way_bill_sent.q4)
        self.assertEquals('2', self.way_bill_sent.q5)
        self.assertEquals('test', self.way_bill_sent.q6)
        self.assertEquals('9', self.way_bill_sent.q7)
        self.assertEquals('Oil', self.way_bill_sent.q8)
        self.assertEquals(400, self.way_bill_sent.q9)


class TestWayBillReceived(unittest.TestCase):
    def setUp(self):
        self.way_bill_received= None
        self.question_code = 'WBR01'
        model_routing_dict[self.question_code]=WayBillReceived


    def tearDown(self):
        if self.way_bill_received is not None:
            self.way_bill_received.delete()

    def test_should_create_WayBillReceived_from_submission_data(self):
        received_date = datetime.strptime('11.11.2011', '%d.%m.%Y')
        waybill_received_submission_data = OrderedDict(
            [('q1', u'pac1'), ('q2', u'2'), ('q3', u'3'), ('q4', u'test'), ('q5', received_date), ('q6', u'2'), ('q7', 3),
                ('q8', 4)])
        crs_custom_report_handler = CRSCustomReportHandler()
        crs_custom_report_handler.handle(self.question_code, waybill_received_submission_data)
        self.way_bill_received = WayBillReceived.objects.get(q1='pac1')
        self.assertEquals('2', self.way_bill_received.q2)
        self.assertEquals('3', self.way_bill_received.q3)
        self.assertEquals('test', self.way_bill_received.q4)
        self.assertEquals(datetime.date(received_date), self.way_bill_received.q5)
        self.assertEquals('2', self.way_bill_received.q6)
        self.assertEquals(3, self.way_bill_received.q7)
        self.assertEquals(4, self.way_bill_received.q8)
