import unittest
from mock import Mock
from datawinners.custom_reports.crs.handler import CRSCustomReportHandler

class TestCRSCustomReportHandler(unittest.TestCase):
    def setUp(self):
        self.submission_data = {}
        self.model_handler_mock = Mock()
        self.crs_routes = {'18': self.model_handler_mock}
        self.handler = CRSCustomReportHandler(self.crs_routes)


    def test_should_route_request_to_appropriate_handler(self):
        self.handler.handle('18', self.submission_data)
        self.model_handler_mock.assert_called_once_with(self.submission_data)

    def test_should_route_ignore_request_if_appropriate_handler_not_found(self):
        self.handler.handle('19', self.submission_data)
        self.assertEquals(0, self.model_handler_mock.call_count)



