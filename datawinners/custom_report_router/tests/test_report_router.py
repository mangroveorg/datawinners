import unittest
from mock import Mock
from datawinners.custom_report_router.report_router import ReportRouter


class TestReportRouter(unittest.TestCase):
    def setUp(self):
        self.form_submission=Mock()
        self.client_specific_custom_report_handler = Mock()
        self.routing_table={'123':self.client_specific_custom_report_handler}

    def test_should_route_to_appropriate_client_handler(self):
        ReportRouter(self.routing_table).route('123', self.form_submission)
        self.client_specific_custom_report_handler.assert_called_once_with(self.form_submission)

    def test_should_not_route_if_organization_handler_is_not_present(self):
        ReportRouter(self.routing_table).route('345',None)
        self.assertEqual(0,self.client_specific_custom_report_handler.call_count)


