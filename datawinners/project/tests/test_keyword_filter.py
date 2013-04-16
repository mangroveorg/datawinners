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
            ['submission_id', 'datasender', ExcelDate(date_contains_keyword, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date, 'dd.mm.yyyy')],
            ['submission_id', 'datasender', ExcelDate(date_contains_keyword, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date_contains_keyword, 'dd.mm.yyyy')],
            ['submission_id', 'datasender', ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date_contains_keyword, 'dd.mm.yyyy')]
        ]

        row_values = [
            ['submission_id', 'datasender', ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date, 'dd.mm.yyyy')],
        ]
        row_values.extend(expected_values)
        filtered_values = keyword_filter.filter(row_values)
        self.assertEqual(expected_values, filtered_values)

    def test_filters_not_applied_for_submission_id(self):
            keyword_filter = KeywordFilter('25')
            date_contains_keyword = datetime.strptime('25.12.2004', '%d.%m.%Y')
            date = datetime.strptime('01.12.2004', '%d.%m.%Y')
            expected_values = [
                ['89848625', 'datasender', ExcelDate(date_contains_keyword, 'dd.mm.yyyy'), 'ans1', 'ans3',
                 ExcelDate(date, 'dd.mm.yyyy')],
                ['submission_id', 'datasender', ExcelDate(date_contains_keyword, 'dd.mm.yyyy'), 'ans1', 'ans3',
                 ExcelDate(date_contains_keyword, 'dd.mm.yyyy')],
                ['12345625', 'datasender', ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
                 ExcelDate(date_contains_keyword, 'dd.mm.yyyy')]
            ]

            row_values = [
                ['12345625', 'datasender', ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
                 ExcelDate(date, 'dd.mm.yyyy')],
            ]
            row_values.extend(expected_values)
            filtered_values = keyword_filter.filter(row_values)
            self.assertEqual(expected_values, filtered_values)

    def test_should_not_filter_by_datasender_mobile_number(self):
        keyword_filter = KeywordFilter('567')
        date = datetime.strptime('01.12.2004', '%d.%m.%Y')
        row_values = [
            ['89848625', ('Shweta', 'rep1', '1234567890'), ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date, 'dd.mm.yyyy')],
            ['submission_id', ('Shweta', 'rep1', '123456890'), ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans3',
             ExcelDate(date, 'dd.mm.yyyy')],
            ['12345625', ('Shweta', 'rep1', '123456890'), ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans567',
             ExcelDate(date, 'dd.mm.yyyy')]
        ]

        expected_values = [
            ['12345625', ('Shweta', 'rep1', '123456890'), ExcelDate(date, 'dd.mm.yyyy'), 'ans1', 'ans567',
             ExcelDate(date, 'dd.mm.yyyy')],
        ]
        filtered_values = keyword_filter.filter(row_values)
        self.assertEqual(expected_values, filtered_values)
