from datawinners.custom_reports.crs.models import PhysicalInventorySheet, WayBillSent, WayBillReceived,\
    crs_model_creator, way_bill_sent_mapping, way_bill_received_mapping, way_bill_sent_by_site_mapping,\
    way_bill_received_by_site_mapping, Distribution, sfm_distribution_mapping, sfe_distribution_mapping,\
    ffa_distribution_mapping, BillOfLading, bill_of_lading_mapping, BreakBulkSent, break_bulk_sent_mapping,\
    WayBillReceivedPort, break_bulk_received_at_port_mapping, ContainerSent, container_sent_mapping,\
    container_received_at_port_mapping, BAV, ffa_bav_mapping, sf_bav_mapping, cps_bav_mapping, cps_bav_defaults,\
    NumberOfRecipientServed, sfm_no_of_recipient_defaults, sfe_no_of_recipient_defaults, cps_no_of_recipient_defaults,\
    ffa_no_of_recipient_defaults, DistributionAtCPS, crs_record_delete, PackingList, packing_list_mapping

from datawinners.custom_reports.crs.models import sfm_distribution_defaults, ffa_distribution_defaults,\
    sfe_distribution_defaults, ffa_bav_defaults

from datawinners.settings import WAYBILL_SENT_QUESTIONNAIRE_CODE, WAYBILL_RECEIVED_QUESTIONNAIRE_CODE,\
    PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE, WAYBILL_SENT_BY_SITE, WAYBILL_RECEIVED_BY_SITE, WAYBILL_RECEIVED_BY_WH,\
    SFM_DISTRIBUTION_CODE, SFE_DISTRIBUTION_CODE, FFA_DISTRIBUTION_CODE, BILL_OF_LADING_QUESTIONNAIRE_CODE,\
    BREAK_BULK_SENT_QUESTIONNAIRE_CODE, BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE, CONTAINER_SENT_QUESTIONNAIRE_CODE,\
    CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE, BAV_FFA_CODE, BAV_SF_CODE, BAV_CPS_CODE, NO_OF_RECIPIENT_SFM_CODE,\
    NO_OF_RECIPIENT_SFE_CODE, NO_OF_RECIPIENT_CPS_CODE, NO_OF_RECIPIENT_FFA_CODE, CPS_DISTRIBUTION_CODE,\
    PACKING_LIST_QUESTIONNAIRE_CODE


model_routing_dict = {
    WAYBILL_SENT_QUESTIONNAIRE_CODE: {'model': WayBillSent, 'question_mapping': way_bill_sent_mapping},
    WAYBILL_SENT_BY_SITE: {'model': WayBillSent, 'question_mapping': way_bill_sent_by_site_mapping},
    WAYBILL_RECEIVED_QUESTIONNAIRE_CODE: {'model': WayBillReceived, 'question_mapping': way_bill_received_mapping},
    WAYBILL_RECEIVED_BY_WH: {'model': WayBillReceived, 'question_mapping': way_bill_received_mapping},
    WAYBILL_RECEIVED_BY_SITE: {'model': WayBillReceived, 'question_mapping': way_bill_received_by_site_mapping},
    PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE: {'model': PhysicalInventorySheet},
    BILL_OF_LADING_QUESTIONNAIRE_CODE: {'model': BillOfLading, 'question_mapping': bill_of_lading_mapping},
    BREAK_BULK_SENT_QUESTIONNAIRE_CODE: {'model': BreakBulkSent, 'question_mapping': break_bulk_sent_mapping},
    BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE: {'model': WayBillReceivedPort,
                                                  'question_mapping': break_bulk_received_at_port_mapping},
    CONTAINER_SENT_QUESTIONNAIRE_CODE: {'model': ContainerSent, 'question_mapping': container_sent_mapping},
    CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE: {'model': WayBillReceivedPort,
                                                 'question_mapping': container_received_at_port_mapping},
    FFA_DISTRIBUTION_CODE: {'model': Distribution, 'question_mapping': ffa_distribution_mapping,
                            'defaults': ffa_distribution_defaults},
    SFE_DISTRIBUTION_CODE: {'model': Distribution, 'question_mapping': sfe_distribution_mapping,
                            'defaults': sfe_distribution_defaults},
    SFM_DISTRIBUTION_CODE: {'model': Distribution, 'question_mapping': sfm_distribution_mapping,
                            'defaults': sfm_distribution_defaults},
    BAV_FFA_CODE: {'model': BAV, 'question_mapping': ffa_bav_mapping, 'defaults': ffa_bav_defaults},
    BAV_CPS_CODE: {'model': BAV, 'question_mapping': cps_bav_mapping, 'defaults': cps_bav_defaults},
    BAV_SF_CODE: {'model': BAV, 'question_mapping': sf_bav_mapping},
    NO_OF_RECIPIENT_SFM_CODE: {'model': NumberOfRecipientServed, 'defaults': sfm_no_of_recipient_defaults},
    NO_OF_RECIPIENT_SFE_CODE: {'model': NumberOfRecipientServed, 'defaults': sfe_no_of_recipient_defaults},
    NO_OF_RECIPIENT_FFA_CODE: {'model': NumberOfRecipientServed, 'defaults': ffa_no_of_recipient_defaults},
    NO_OF_RECIPIENT_CPS_CODE: {'model': NumberOfRecipientServed, 'defaults': cps_no_of_recipient_defaults},
    CPS_DISTRIBUTION_CODE: {'model': DistributionAtCPS},
    PACKING_LIST_QUESTIONNAIRE_CODE: {'model': PackingList, 'question_mapping': packing_list_mapping},
}

class CRSCustomReportHandler(object):
    def __init__(self, routing_dict=None):
        self.routing_dict = routing_dict or model_routing_dict

    def handle(self, form_code, submission_data, data_record_id):
        dictionary = self.routing_dict.get(form_code)
        if dictionary:
            crs_model_creator(data_record_id, submission_data, dictionary.get('model'),
                dictionary.get('question_mapping'), dictionary.get('defaults'))

    def delete_handler(self, form_code, data_record_id):
        dictionary = self.routing_dict.get(form_code)
        if dictionary:
            crs_record_delete(data_record_id, dictionary.get('model'))

