from datetime import datetime
import unittest
from mock import Mock
from datawinners.project.export_to_excel import format_field_values_for_excel
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import IntegerField, GeoCodeField, DateField, SelectField, ExcelDate
from mangrove.form_model.form_model import FormModel

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

    def test_geo_field_returns_number(self):
        form_model = Mock(spec=FormModel)
        row = [{'geocode': '-13.235467,12.21267348'}]
        form_model.get_field_by_code_and_rev.return_value = GeoCodeField(label="What is your gps?", code="GPS",
            name="What is your gps?", ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual((-13.235467, 12.21267348), formatted_dict['geocode'])

    def test_longitude_geo_field_not_provided_returns_empty(self):
        form_model = Mock(spec=FormModel)
        row = [{'geocode': 'incorrect_geo_code'}]
        form_model.get_field_by_code_and_rev.return_value = GeoCodeField(label="What is your gps?", code="GPS",
            name="What is your gps?", ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual(('incorrect_geo_code', ''), formatted_dict['geocode'])

    def test_lat_geo_field_not_provided_returns_empty(self):
        form_model = Mock(spec=FormModel)
        row = [{'geocode': ',incorrect_geo_code'}]
        form_model.get_field_by_code_and_rev.return_value = GeoCodeField(label="What is your gps?", code="GPS",
            name="What is your gps?", ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual(('', 'incorrect_geo_code'), formatted_dict['geocode'])

    def test_error_date_field_returns_string(self):
        form_model = Mock(spec=FormModel)
        row = [{'date': 'some_string'}]
        form_model.get_field_by_code_and_rev.return_value = DateField(label="Report date", code="RD",
            name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual('some_string', formatted_dict['date'])

    def test_date_values_returned_as_date_type_objects(self):
        self._test_date('31.03.1999', 'dd.mm.yyyy', '%d.%m.%Y')

    def test_month_year_string_returned_as_date_type_objects(self):
        self._test_date('03.1999', 'mm.yyyy', '%m.%Y')

    def _test_date(self, date_as_string, date_field_format, date_format):
        form_model = Mock(spec=FormModel)
        row = [{'date': date_as_string}]
        form_model.get_field_by_code_and_rev.return_value = DateField(label="Report date", code="RD",
            name="What is reporting date?", date_format=date_field_format,
            event_time_field_flag=True, ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        expected_date = datetime.strptime(date_as_string, date_format)
        self.assertEqual(ExcelDate(expected_date ,date_field_format), formatted_dict['date'])

    def test_get_option_value_for_select_field(self):
        form_model = Mock(spec=FormModel)
        row = [{'select': 'a'}]
        form_model.get_field_by_code_and_rev.return_value = SelectField(label="What is your blood group?",
            code="select", name="What is your blood group?",
            options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")], single_select_flag=False,
            ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual(['one'], formatted_dict['select'])

    def test_get_multiple_option_value_for_select_field(self):
        form_model = Mock(spec=FormModel)
        row = [{'select': 'ab'}]
        form_model.get_field_by_code_and_rev.return_value = SelectField(label="What is your blood group?",
            code="select", name="What is your blood group?",
            options=[("one", "a"), ("two", "b"), ("three", "c"), ("four", "d")], single_select_flag=False,
            ddtype=Mock(spec=DataDictType))
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual(['one', 'two'], formatted_dict['select'])

    def test_should_return_a_string_if_field_does_not_exist(self):
        form_model = Mock(spec=FormModel)
        row = [{'reporting_date': '31.03.1999'}]
        form_model.get_field_by_code_and_rev.return_value = None
        formatted_dict = format_field_values_for_excel(row, form_model)
        self.assertEqual('31.03.1999',formatted_dict['reporting_date'])
