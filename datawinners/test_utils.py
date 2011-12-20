# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datetime import datetime
from django.test.client import RequestFactory
from mock import Mock
import utils
from pytz import UTC

class TestUtils(unittest.TestCase):

    def test_should_generate_excel_sheet(self):
        raw_data = [["cid002", 'shweta', 55], ["cid001", 'asif', 35]]
        header_list = ["field1", "field2", 'field3']
        raw_data.insert(0,header_list)
        sheet_name = 'test'
        wb = utils.get_excel_sheet(raw_data, sheet_name)
        self.assertEquals(3, len(wb.get_sheet(0).rows))
        self.assertEquals(3, wb.get_sheet(0).row(0).get_cells_count())

    def test_should_write_date_value_to_excel_sheet(self):
         date = datetime(2011, 6, 22, 5, 20, 43, 661771, tzinfo=UTC)
         raw_data = [["cid002", 'shweta', date], ["cid001", 'asif', date]]
         wb = utils.get_excel_sheet(raw_data, "test")
         self.assertEquals(2, len(wb.get_sheet(0).rows))
         self.assertEquals(3, wb.get_sheet(0).row(0).get_cells_count())

    def test_should_return_organization(self):
        org_id = 'SLX364903'
        request = self._get_request_mock(org_id)

        organization = utils.get_organization(request)
        self.assertEquals(org_id,organization.org_id)

    def test_convert_to_ordinal(self):
        self.assertEquals('12th',utils.convert_to_ordinal(12))
        self.assertEquals('21st',utils.convert_to_ordinal(21))
        self.assertEquals('32nd',utils.convert_to_ordinal(32))
        self.assertEquals('43rd',utils.convert_to_ordinal(43))
        self.assertEquals('77th',utils.convert_to_ordinal(77))

    def test_generate_document_store(self):
        self.assertEquals(u'hni_abc_1234', utils.generate_document_store_name(u'abc',u'1234'))

    def _get_request_mock(self,org_id):
        request = RequestFactory().get('/account/')
        request.user = Mock()
        mock_profile = Mock()
        mock_profile.org_id = Mock(return_value=org_id)
        request.user.get_profile = Mock(return_value=mock_profile)
        return request
