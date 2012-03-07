from datawinners.custom_reports.crs.models import waybillsent_handler
from datawinners.custom_reports.crs.models import waybillreceived_handler
from datawinners.local_settings import WAYBILL_SENT_QUESTIONNAIRE_CODE, WAYBILL_RECEIVED_QUESTIONNAIRE_CODE

model_routing_dict = {WAYBILL_SENT_QUESTIONNAIRE_CODE: waybillsent_handler, WAYBILL_RECEIVED_QUESTIONNAIRE_CODE: waybillreceived_handler}

class CRSCustomReportHandler(object):
    def __init__(self, routing_dict=None):
        self.routing_dict = routing_dict or model_routing_dict


    def handle(self, form_code, submission_data):
        crs_model_creater = self.routing_dict.get(form_code, self.dummy_handler)
        crs_model_creater(submission_data)

    def dummy_handler(self, submission_data):
        pass


