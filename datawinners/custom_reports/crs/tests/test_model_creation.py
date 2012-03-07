import unittest
from collections import OrderedDict
from datawinners.custom_reports.crs.handler import CRSCustomReportHandler
from datawinners.custom_reports.crs.models import WayBillSent, WayBillReceived

class TestWayBillSent(unittest.TestCase):
    def setUp(self):
        self.way_bill_sent = None

    def tearDown(self):
        if self.way_bill_sent is not None:
            self.way_bill_sent.delete()

    def test_should_create_WayBillSent_from_submission_data(self):
        waybill_sent_submission_data = OrderedDict(
            [('q1', u'pac1'), ('q2', u'2'), ('q3', '11.11.2011'), ('q4', u'Transfer'), ('q5', u'2'),
                ('q6', u'test'), ('q7', u'9'), ('q8', u'Oil'), ('q9', 400)])
        crs_custom_report_handler = CRSCustomReportHandler()
        waybill_sent_questionnaire_form_code = '18'
        crs_custom_report_handler.handle(waybill_sent_questionnaire_form_code, waybill_sent_submission_data)
        self.way_bill_sent = WayBillSent.objects.get(pl_code='pac1')
        self.assertEquals('2', self.way_bill_sent.waybill_code)
        self.assertEquals('11.11.2011', self.way_bill_sent.sent_date)
        self.assertEquals('Transfer', self.way_bill_sent.transaction_type)
        self.assertEquals('2', self.way_bill_sent.site_code)
        self.assertEquals('test', self.way_bill_sent.sender_name)
        self.assertEquals('Oil', self.way_bill_sent.food_type)
        self.assertEquals(400, self.way_bill_sent.weight)


class TestWayBillReceived(unittest.TestCase):
    def setUp(self):
        self.way_bill_received= None

    def tearDown(self):
        if self.way_bill_received is not None:
            self.way_bill_received.delete()

    def test_should_create_WayBillReceived_from_submission_data(self):
        waybill_received_submission_data = OrderedDict(
            [('q1', u'pac1'), ('q2', u'2'), ('q3', u'3'), ('q4', u'test'), ('q5', u'11.11.2011'), ('q6', u'2'), ('q7', 3),
                ('q8', 4)])
        crs_custom_report_handler = CRSCustomReportHandler()
        waybill_received_questionnaire_form_code = '20'
        crs_custom_report_handler.handle(waybill_received_questionnaire_form_code, waybill_received_submission_data)
        self.way_bill_received = WayBillReceived.objects.get(pl_code='pac1')
        self.assertEquals('2', self.way_bill_received.waybill_code)
        self.assertEquals('3', self.way_bill_received.site_code)
        self.assertEquals('test', self.way_bill_received.receiver_name)
        self.assertEquals('11.11.2011', self.way_bill_received.received_date)
        self.assertEquals('2', self.way_bill_received.truck_id)
        self.assertEquals(3, self.way_bill_received.good_net_weight)
        self.assertEquals(4, self.way_bill_received.damaged_net_weight)
