from django.test.testcases import TestCase
from datawinners.entity.fields import PhoneNumberField, DjangoDateField
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

class TestDateField(TestCase):
    def test_should_validate_date(self):
        invalid_dates = {
            "29.02.2011": [u'Enter a valid date.'],
             "12/02/2011": [u'Enter a valid date.'],
             "29.14.2011": [u'Enter a valid date.'],
             }
        valid_dates = {
            "29.02.2012": "29.02.2012",
            "31.12.1999": "31.12.1999",
            "  11.03.2012  ": "11.03.2012",
            }
        field_kwargs = {"input_formats": ("%d.%m.%Y",)}
        assertFieldOutput(self, DjangoDateField, {}, invalid_dates, field_kwargs=field_kwargs, empty_value=None)
        assertFieldOutput(self, DjangoDateField, valid_dates, {}, field_kwargs=field_kwargs, empty_value=None)
