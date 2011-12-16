# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datetime import datetime
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
  