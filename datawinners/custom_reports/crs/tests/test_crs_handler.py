import unittest
from mock import Mock, patch
from datawinners.custom_reports.crs.handler import CRSCustomReportHandler

class TestCRSCustomReportHandler(unittest.TestCase):
    def setUp(self):
        self.submission_data = {}
        self.model_mock = Mock()
        self.mapping = Mock(spec=dict)
        self.crs_routes = {'18': {'model':self.model_mock, 'question_mapping':self.mapping}}
        self.handler = CRSCustomReportHandler(self.crs_routes)



    def test_should_route_request_to_appropriate_handler(self):
        with patch("datawinners.custom_reports.crs.handler.crs_model_creator") as crs_model_creator_mock:
            self.handler.handle('18', self.submission_data)
            crs_model_creator_mock.assert_called_once_with(self.submission_data,self.model_mock,self.mapping)


    def test_should_route_ignore_request_if_appropriate_handler_not_found(self):
        with patch("datawinners.custom_reports.crs.handler.crs_model_creator") as crs_model_creator_mock:
            self.handler.handle('19', self.submission_data)
            self.assertEquals(0, crs_model_creator_mock.call_count)



