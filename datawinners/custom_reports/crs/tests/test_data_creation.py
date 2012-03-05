import unittest
from unittest.case import SkipTest
from datawinners.custom_reports.crs.models import WayBillSent, WayBillReceived
from datetime import datetime

@SkipTest
# temp test cases to create test data
class TestDataCreation(unittest.TestCase):

    def test_way_bill_test_data_creation(self):
        self.no_csb_lost()
        self.damaged_and_lost_rice()
        self.damaged_csb()
        self.in_transit_oil()

    def no_csb_lost(self):
        way_bill_sent = WayBillSent(pl_code='1840', waybill_code='TVE105', sent_date=datetime.now(),
            transaction_type='Transfert to  CRS warehouses', site_code='TVE1', sender_name='David', truck_id='3810TV',
            food_type='CSB', weight=2490)
        way_bill_received = WayBillReceived(pl_code='1840', waybill_code='TVE105', received_date=datetime.now(),
            site_code='FNR1'
            , receiver_name='JOELSON', truck_id='3810TV', good_net_weight=2490, damaged_net_weight=0)
        way_bill_sent.save()
        way_bill_received.save()

    def damaged_and_lost_rice(self):
        way_bill_sent = WayBillSent(pl_code='1840', waybill_code='TNR004', sent_date=datetime.now(),
            transaction_type='Transfert to  CRS warehouses', site_code='TNR1', sender_name='Njaka', truck_id='2510TU',
            food_type='Rice', weight=10000)
        way_bill_received = WayBillReceived(pl_code='1840', waybill_code='TNR004', received_date=datetime.now(),
            site_code='FTU1'
            , receiver_name='Rakoto', truck_id='2510TU', good_net_weight=7750, damaged_net_weight=1500)
        way_bill_sent.save()
        way_bill_received.save()

    def damaged_csb(self):
        way_bill_sent = WayBillSent(pl_code='1840', waybill_code='TVE050', sent_date=datetime.now(),
            transaction_type='Delivery to SFM', site_code='TVE1', sender_name='David', truck_id='1818AE',
            food_type='CSB', weight=250)
        way_bill_received = WayBillReceived(pl_code='1840', waybill_code='TVE050', received_date=datetime.now(),
            site_code='12BRTSFMTNB03'
            , receiver_name='Jean', truck_id='1818AE', good_net_weight=225, damaged_net_weight=25)
        way_bill_sent.save()
        way_bill_received.save()

    def in_transit_oil(self):
        way_bill_sent = WayBillSent(pl_code='1840', waybill_code='TVE110', sent_date=datetime.now(),
            transaction_type='Transfert to  CRS warehouses', site_code='TVE1', sender_name='David', truck_id='1818AE',
            food_type='OIL', weight=925)
        way_bill_sent.save()
