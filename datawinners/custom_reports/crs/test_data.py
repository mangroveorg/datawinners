from datetime import date
import random
import string
from dateutil.relativedelta import relativedelta
from datawinners.custom_reports.crs.models import ContainerSent, PackingList, BillOfLading, BreakBulkSent, WayBillReceivedPort, WayBillSent, WayBillReceived, Distribution

def generate_id(id_length):
    return ''.join([random.choice(string.digits + string.letters) for i in range(id_length)])

class PackingListBuilder():
    def build(self):
        packing_list = PackingList()
        packing_list.q1 = 'PL' + generate_id(8)
        packing_list.q2 = 100
        packing_list.q3 = 100
        packing_list.q4 = 100
        packing_list.q5 = 100
        return packing_list

class BillOfLadingBuilder():
    def build(self, pl_code, issue_date, food_type, shipment_type):
        bill_of_lading = BillOfLading()
        bill_of_lading.q1 = pl_code
        bill_of_lading.q2 = shipment_type
        bill_of_lading.q3 = issue_date
        bill_of_lading.q4 = food_type
        bill_of_lading.q5 = 'BL' + generate_id(8)
        bill_of_lading.q6 = total_shipment
        bill_of_lading.q7 = total_shipment
        bill_of_lading.q8 = 'ccc'
        bill_of_lading.q9 = 100
        return bill_of_lading

class ContainerSentBuilder():
    def build(self, bl_code):
        container_sent = ContainerSent()
        container_sent.q1 = bl_code
        container_sent.q2 = container_capacity
        container_sent.q3 = generate_id(4)
        return container_sent

class BreakBulkSentBuilder():
    def build(self, sent_date, pl_code, food_type):
        break_bulk_sent = BreakBulkSent()
        break_bulk_sent.q1 = sent_date
        break_bulk_sent.q2 = break_bulk_capacity
        break_bulk_sent.q3 = 'BB' + generate_id(8)
        break_bulk_sent.q4 = pl_code
        break_bulk_sent.q5 = food_type
        return break_bulk_sent


class WayBillReceivedPortBuilder():
    def build(self, waybill_code, received_date, weight, container_code):
        way_bill_received_port = WayBillReceivedPort()
        way_bill_received_port.q1 = waybill_code
        way_bill_received_port.q2 = received_date
        way_bill_received_port.q3 = weight
        way_bill_received_port.q4 = 0
        way_bill_received_port.q5 = container_code
        way_bill_received_port.q6 = 'WH' + generate_id(8)
        return way_bill_received_port

class WayBillSentBuilder():
    def build(self,pl_code,sent_date,source_warehouse,food_type):
        way_bill_sent = WayBillSent()
        way_bill_sent.q1 = pl_code
        way_bill_sent.q2 = "WB"+generate_id(5)
        way_bill_sent.q3 = sent_date
        way_bill_sent.q4 = 'Transfert aux magasins de CRS'
        way_bill_sent.q5 = source_warehouse
        way_bill_sent.q6 = "Sender"
        way_bill_sent.q7 = "TruckID"
        way_bill_sent.q8 = food_type
        way_bill_sent.q9 = container_capacity
        way_bill_sent.q10 = "receiver"+generate_id(3)
        return way_bill_sent

    def _trnx_type(self, food_type):
        csb_types = ['Livraisons pour SFM','Livraisons pour SFE']
        sorgho_type = 'Livraisons pour FFA'
        oil_types = ['Livraisons pour SFM','Livraisons pour SFE', sorgho_type]
        if food_type == 'SORGHO' :
            return sorgho_type
        if food_type == 'HUILE':
            return random.choice(oil_types)
        return random.choice(csb_types)

    def build_sent_to_site(self, pl_code, sent_date, source_warehouse, food_type):
        way_bill = self.build(pl_code, sent_date, source_warehouse, food_type)
        way_bill.q4 = self._trnx_type(food_type)
        return way_bill

class WayBillReceivedBuilder():
     def build(self,pl_code,waybill_code,received_date):
        way_bill_received = WayBillReceived()
        way_bill_received.q1 = pl_code
        way_bill_received.q2 = waybill_code
        way_bill_received.q3 = "WH"+generate_id(5)
        way_bill_received.q4 = "Receiver"
        way_bill_received.q5 = received_date
        way_bill_received.q6 = "TruckID"
        way_bill_received.q7 = container_capacity
        way_bill_received.q8 = 0
        way_bill_received.q9 = 'CRS received from stores'
        return way_bill_received


class DistributionBuilder():
    def build(self,site_code,dist_date,way_bill_code):
        distribution = Distribution()
        distribution.q1 = site_code
        distribution.q2 = dist_date
        distribution.q3 = way_bill_code
        distribution.q4 = ''
        distribution.q5 = 1000
        distribution.q6 = 1000
        distribution.q7 = 1000
        distribution.q8 = 1000
        distribution.distribution_type = 'SFM'
        return distribution




def send_containers_to_warehouse(food_type, pl_code, shipping_date):
        bill_of_lading = BillOfLadingBuilder().build(pl_code, shipping_date, food_type, 'CONTAINER')
        bill_of_lading.save()
        for i in range(total_shipment / container_capacity):
            if not i % 100:
                print i
            container_sent = ContainerSentBuilder().build(bill_of_lading.q5)
            container_sent.save()
            way_bill_received_port = WayBillReceivedPortBuilder().build('', shipping_date, container_sent.q2, container_sent.q3)
            way_bill_received_port.save()

            way_bill_sent = WayBillSentBuilder().build(pl_code,shipping_date,way_bill_received_port.q6,food_type)
            way_bill_sent.save()
            way_bill_received = WayBillReceivedBuilder().build(pl_code,way_bill_sent.q2,shipping_date)
            way_bill_received.save()

            distribution_shipping_date = shipping_date + relativedelta(days=+2)
            way_bill_sent_to_site = WayBillSentBuilder().build_sent_to_site(pl_code, distribution_shipping_date,way_bill_received.q3,food_type)
            way_bill_sent_to_site.save()
            way_bill_received_by_site = WayBillReceivedBuilder().build(pl_code,way_bill_sent_to_site.q2,distribution_shipping_date)
            way_bill_received_by_site.save()
            distribution = DistributionBuilder().build(way_bill_received_by_site.q3,distribution_shipping_date,way_bill_received_by_site.q2)
            distribution.save()

def send_break_bulk_to_warehouse(food_type, pl_code, shipping_date):
        bill_of_lading = BillOfLadingBuilder().build(pl_code, shipping_date, food_type, 'BREAK BULK')
        bill_of_lading.save()
        for i in range(total_shipment / break_bulk_capacity):
            if not i % 100:
                print i
            break_bulk_sent = BreakBulkSentBuilder().build(shipping_date, pl_code, food_type)
            break_bulk_sent.save()
            WayBillReceivedPortBuilder().build(break_bulk_sent.q3, shipping_date, break_bulk_sent.q2, '').save()


def tear_down():
    models = [ContainerSent, PackingList, BillOfLading, BreakBulkSent, WayBillReceivedPort, WayBillSent, WayBillReceived, Distribution]
    [model.objects.all().delete() for model in models]


def container_shipment(commodities, base_date):
    shipping_date = base_date
    packing_list = PackingListBuilder().build()
    packing_list.save()
    pl_code = packing_list.q1
    for food_type in commodities:
        send_containers_to_warehouse(food_type, pl_code, shipping_date)


def break_bulk_shipment(commodities, base_date):
    shipping_date = base_date + relativedelta(months=+1)
    packing_list = PackingListBuilder().build()
    packing_list.save()
    pl_code = packing_list.q1
    for food_type in commodities:
        send_break_bulk_to_warehouse(food_type, pl_code, shipping_date)

container_capacity = 100
break_bulk_capacity = 100
total_shipment = 100000

def create_one_set():
    tear_down()
    commodities = ['RIZ', 'HUILE', 'CSB', 'SORGHO']
    base_date = date(2001, 1, 1)
    shipments = [base_date,base_date+relativedelta(months=3),base_date+relativedelta(months=6),base_date+relativedelta(months=9)]

    for shipment_date in shipments:
        print "----     ----    ----\n"
        container_shipment(commodities, shipment_date)
        break_bulk_shipment(commodities, shipment_date)