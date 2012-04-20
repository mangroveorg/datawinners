from datawinners.custom_reports.crs.models import PhysicalInventorySheet, WayBillSent, WayBillReceived, \
    crs_model_creator, way_bill_sent_mapping, way_bill_received_mapping, way_bill_sent_by_site_mapping, \
    way_bill_received_by_site_mapping, Distribution, sfm_distribution_mapping, sfe_distribution_mapping, \
    ffa_distribution_mapping, BillOfLading, bill_of_lading_mapping, BreakBulkSent, break_bulk_sent_mapping, \
    WayBillReceivedPort, break_bulk_received_at_port_mapping, ContainerSent, container_sent_mapping,\
    container_received_at_port_mapping
from datawinners.custom_reports.crs.models import sfm_distribution_defaults, ffa_distribution_defaults, \
    sfe_distribution_defaults
from datawinners.settings import WAYBILL_SENT_QUESTIONNAIRE_CODE, WAYBILL_RECEIVED_QUESTIONNAIRE_CODE,\
    PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE, WAYBILL_SENT_BY_SITE, WAYBILL_RECEIVED_BY_SITE, WAYBILL_RECEIVED_BY_WH, \
    SFM_DISTRIBUTION_CODE, SFE_DISTRIBUTION_CODE, FFA_DISTRIBUTION_CODE, BILL_OF_LADING_QUESTIONNAIRE_CODE,\
    BREAK_BULK_SENT_QUESTIONNAIRE_CODE, BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE, CONTAINER_SENT_QUESTIONNAIRE_CODE,\
    CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE

model_routing_dict = {
    WAYBILL_SENT_QUESTIONNAIRE_CODE: {'model': WayBillSent, 'question_mapping': way_bill_sent_mapping},
    WAYBILL_SENT_BY_SITE: {'model': WayBillSent, 'question_mapping': way_bill_sent_by_site_mapping},
    WAYBILL_RECEIVED_QUESTIONNAIRE_CODE: {'model': WayBillReceived, 'question_mapping': way_bill_received_mapping},
    WAYBILL_RECEIVED_BY_WH: {'model': WayBillReceived, 'question_mapping': way_bill_received_mapping},
    WAYBILL_RECEIVED_BY_SITE: {'model': WayBillReceived, 'question_mapping': way_bill_received_by_site_mapping},
    PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE: {'model' : PhysicalInventorySheet},
    BILL_OF_LADING_QUESTIONNAIRE_CODE: {'model' : BillOfLading, 'question_mapping': bill_of_lading_mapping},
    BREAK_BULK_SENT_QUESTIONNAIRE_CODE: {'model' : BreakBulkSent, 'question_mapping': break_bulk_sent_mapping},
    BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE : {'model' : WayBillReceivedPort, 'question_mapping': break_bulk_received_at_port_mapping},
    CONTAINER_SENT_QUESTIONNAIRE_CODE : {'model' : ContainerSent, 'question_mapping': container_sent_mapping},
    CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE:{'model' : WayBillReceivedPort, 'question_mapping': container_received_at_port_mapping},
    FFA_DISTRIBUTION_CODE: {'model': Distribution, 'question_mapping': ffa_distribution_mapping, 'defaults': ffa_distribution_defaults},
    SFE_DISTRIBUTION_CODE: {'model': Distribution, 'question_mapping': sfe_distribution_mapping, 'defaults': sfe_distribution_defaults},
    SFM_DISTRIBUTION_CODE: {'model': Distribution, 'question_mapping': sfm_distribution_mapping, 'defaults': sfm_distribution_defaults}
}

class CRSCustomReportHandler(object):
    def __init__(self, routing_dict=None):
        self.routing_dict = routing_dict or model_routing_dict


    def handle(self, form_code, submission_data):
        dictionary = self.routing_dict.get(form_code)
        if dictionary :
            crs_model_creator(submission_data, dictionary.get('model'),dictionary.get('question_mapping'), dictionary.get('defaults'))
