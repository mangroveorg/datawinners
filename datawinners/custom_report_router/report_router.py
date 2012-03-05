class ReportRouter(object):
    def __init__(self, routing_table):
        self.routing_table = routing_table

    def route(self, organization_id, form_submission):
        custom_report_handler = self.routing_table.get(organization_id, self.fake_custom_report_handler)
        custom_report_handler(form_submission)


    def fake_custom_report_handler(self,form_submission):
        pass

