import unittest
from mock import Mock
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import IntegerField, GeoCodeField, DateField
from mangrove.form_model.form_model import FormModel
from project.export_to_excel import format_field_values_for_excel

class TestExportToExcel(unittest.TestCase):
    def test_error_integer_field_returns_string(self):
        form_model = Mock(spec=FormModel)
        expected_value = 'incorrect_Integer_Value'
        row = [{'int': expected_value}]
        form_model.get_field_by_code_and_rev.return_value = IntegerField(label="Fathers age", code="FA",
            name="Zhat is your father's age?",
            ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual(expected_value, formatted_dict['int'])

    def test_error_geo_field_returns_string(self):
        form_model = Mock(spec=FormModel)
        row = [{'geocode': 'incorrect_geo_code,12.2'}]
        form_model.get_field_by_code_and_rev.return_value = GeoCodeField(label="What is your gps?", code="GPS",
            name="What is your gps?", ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual('incorrect_geo_code', formatted_dict['GPS_lat'])
        self.assertEqual('12.2', formatted_dict['GPS_long'])

    def test_error_date_field_returns_string(self):
        form_model = Mock(spec=FormModel)
        row = [{'date': 'some_string'}]
        form_model.get_field_by_code_and_rev.return_value = DateField(label="Report date", code="RD",
            name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual('some_string', formatted_dict['date'])

    def test_date_field_no_format_validation(self):
        form_model = Mock(spec=FormModel)
        row = [{'date_format_mm_yyyy_dd': '03_2012_23'}]
        form_model.get_field_by_code_and_rev.return_value = DateField(label="Report date", code="RD",
            name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual('03_2012_23', formatted_dict['date_format_mm_yyyy_dd'])
