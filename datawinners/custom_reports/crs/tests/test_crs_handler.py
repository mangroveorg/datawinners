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
        self.data_record_id = 'data_rec_id'



    def test_should_route_request_to_appropriate_handler(self):
        with patch("datawinners.custom_reports.crs.handler.crs_model_creator") as crs_model_creator_mock:
            self.handler.handle('18', self.submission_data,self.data_record_id)
            crs_model_creator_mock.assert_called_once_with(self.data_record_id,self.submission_data,self.model_mock,self.mapping, None)

    def test_should_route_request_to_delete_handler(self):
        with patch("datawinners.custom_reports.crs.handler.crs_record_delete") as crs_model_delete:
            self.handler.delete_handler('18',self.data_record_id)
            crs_model_delete.assert_called_once_with(self.data_record_id,self.model_mock)


    def test_should_route_ignore_request_if_appropriate_handler_not_found(self):
        with patch("datawinners.custom_reports.crs.handler.crs_model_creator") as crs_model_creator_mock:
            self.handler.handle('19', self.submission_data,self.data_record_id)
            self.assertEquals(0, crs_model_creator_mock.call_count)



