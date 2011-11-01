from django.test.testcases import TestCase
from datawinners.entity.fields import PhoneNumberField, EMPTY_VALUES
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

