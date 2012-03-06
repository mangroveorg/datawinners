from mangrove.utils.types import  is_not_empty

class ReportRouter(object):
    def __init__(self, routing_table):
        self.routing_table = routing_table


    def route(self, organization_id, form_submission):
        if self.has_error_in_submission(form_submission): return
        custom_report_handler = self.routing_table.get(organization_id, self.fake_custom_report_handler)
        custom_report_handler(form_submission)


    def has_error_in_submission(self, form_submission):
        return is_not_empty(form_submission.errors)

    def fake_custom_report_handler(self, form_submission):
        pass

