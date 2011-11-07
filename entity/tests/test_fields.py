from django.test.testcases import TestCase
from mock import Mock
from datawinners.entity.fields import PhoneNumberField, EMPTY_VALUES, PhoneCountryCodeSelect, PhoneCountryCodeSelectField
from datawinners.tests.backport import assertFieldOutput


class TestPhoneNumberField(TestCase):
    def test_should_validate_and_clean_phone_numbers(self):
        valid_cases = {
            '1112223333': '1112223333',
            ' 1112223333 ': '1112223333',
            '111-222-3333': '1112223333',
            '111 222 3333': '1112223333',
            '1-11222-3333': '1112223333',
            '(123) 456-7890': '1234567890',
            '(1233) 456-7890': '12334567890',
            }
        invalid_cases = {
            '23': ['Ensure this value has at least 5 digits (it has 2).'],
            '1--23': ['Ensure this value has at least 5 digits (it has 3).'],
            '1111222233334444': ['Ensure this value has at most 15 characters (it has 16).'],
            'abcdefgh': ['Please enter a valid phone number.'],
            '^6506368600': ['Please enter a valid phone number.'],
            }

        assertFieldOutput(self, PhoneNumberField, valid_cases, {})
        assertFieldOutput(self, PhoneNumberField, {}, invalid_cases)

    def test_should_show_right_html_for_phone_countrycode_select(self):
        phone_counry_select = PhoneCountryCodeSelect()
        html_return_value = phone_counry_select.render_option(selected_choices='', option_value='sth',
                                                              option_label="whatever")
        self.assertEqual(u'<option value="sth" title="whatever" >whatever sth</option>', html_return_value)

    def test_should_get_right_data_from_phone_countrycode_select_field(self):
        phone_country_code_select_field = PhoneCountryCodeSelectField()
        self.assertIsInstance(phone_country_code_select_field.widget, PhoneCountryCodeSelect)

    def test_clean_with_phone_country_code_select_field_should_return_value_with_country_code(self):
        phone_number_field = PhoneNumberField()
        phone_country_code_select_field = PhoneCountryCodeSelectField(data_for=phone_number_field)
        phone_country_code_select_field.clean('+86')
        self.assertEqual(phone_number_field.country_code, u'+86')

    def test_clean_with_phone_number_field_should_return_value_with_country_code(self):
        phone_number_field = PhoneNumberField()
        phone_number_field.country_code = '+86'
        self.assertEqual(phone_number_field.clean('111222'), u'+86111222')
