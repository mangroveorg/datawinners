import unittest
from mock import Mock
from datawinners.custom_report_router.report_router import ReportRouter, custom_report_routing_table


class TestReportRouter(unittest.TestCase):
    def setUp(self):
        self.form_submission=Mock()
        self.client_specific_custom_report_handler = Mock()
        self.org_id_for_custom_report = '123'
        custom_report_routing_table.update({'123':self.client_specific_custom_report_handler})
        self.form_submission.errors = None

    def test_should_route_to_appropriate_client_handler(self):
        ReportRouter().route(self.org_id_for_custom_report, self.form_submission)
        self.client_specific_custom_report_handler.assert_called_once_with(self.form_submission)

    def test_should_not_route_if_organization_handler_is_not_present(self):
        ReportRouter().route('345',self.form_submission)
        self.assertEqual(0,self.client_specific_custom_report_handler.call_count)

    def test_should_not_call_client_handler_if_errors_exist_in_form_submission(self):
        self.form_submission.errors = ["some error"]
        ReportRouter().route(self.org_id_for_custom_report,self.form_submission)
        self.assertEqual(0,self.client_specific_custom_report_handler.call_count)







