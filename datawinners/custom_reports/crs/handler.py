from datawinners.custom_reports.crs.models import PhysicalInventorySheet, WayBillSent, WayBillReceived, crs_model_creator
from datawinners.local_settings import WAYBILL_SENT_QUESTIONNAIRE_CODE, WAYBILL_RECEIVED_QUESTIONNAIRE_CODE,\
    PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE

model_routing_dict = {
    WAYBILL_SENT_QUESTIONNAIRE_CODE: WayBillSent,
    WAYBILL_RECEIVED_QUESTIONNAIRE_CODE: WayBillReceived,
    PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE: PhysicalInventorySheet,
}

class CRSCustomReportHandler(object):
    def __init__(self, routing_dict=None):
        self.routing_dict = routing_dict or model_routing_dict


    def handle(self, form_code, submission_data):
        crs_model_creator(submission_data, model_routing_dict.get(form_code))

    def dummy_handler(self, submission_data):
        pass


