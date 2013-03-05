from datetime import datetime
import unittest

from mangrove.form_model.field import ExcelDate
from project.filters import KeywordFilter

class TestKeywordFilter(unittest.TestCase):
    def test_filters_applied_when_exporting_data(self):
        keyword_filter = KeywordFilter('25')
        date_contains_keyword = datetime.strptime('25.12.2004', '%d.%m.%Y')
        date = datetime.strptime('01.12.2004', '%d.%m.%Y')
        expected_values = [
            ['datasender', ExcelDate(date_contains_keyword, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date, 'dd.mm.yyyy')],
            ['datasender', ExcelDate(date_contains_keyword, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date_contains_keyword, 'dd.mm.yyyy')],
            ['datasender', ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date_contains_keyword, 'dd.mm.yyyy')]
        ]

        row_values = [
            ['datasender', ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3', ExcelDate(date, 'dd.mm.yyyy')],
        ]
        row_values.extend(expected_values)
        filtered_values = keyword_filter.filter(row_values)
        self.assertEqual(expected_values, filtered_values)


