from mangrove.utils.types import  is_not_empty, is_empty


custom_report_routing_table={}

class ReportRouter(object):

    def route(self, organization_id, form_submission):
        if self.has_error_in_submission(form_submission): return
        custom_report_handler = custom_report_routing_table.get(organization_id, self.fake_custom_report_handler)
        custom_report_handler(form_submission.form_code,form_submission.processed_data)

    def has_error_in_submission(self, form_submission):
        return is_not_empty(form_submission.errors)

    def fake_custom_report_handler(self, code, data):
        pass

