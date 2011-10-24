from django.test.testcases import TestCase
from datawinners.entity.fields import PhoneNumberField, EMPTY_VALUES
from datawinners.tests.backport import assertFieldOutput


class TestPhoneNumberField(TestCase):
    def test_should_validate_and_clean_phone_numbers(self):
        valid_cases = {
            '1112223333': '1112223333',
            '111-222-3333': '1112223333',
            '650-636-8600': '6506368600',
            '6-50636-8600': '6506368600',
            '+1-541-754-3010': '+15417543010',
            }
        invalid_cases = {
            '23': ['Ensure this value has at least 5 characters (it has 2).'],
            '2234232423422433': ['Ensure this value has at most 15 characters (it has 16).'],
            'abcdefgh': ['Please enter a valid phone number.'],
            '650 636 8600': ['Please enter a valid phone number.'],
            '(650)6368600': ['Please enter a valid phone number.'],
            '^6506368600': ['Please enter a valid phone number.'],
            }
        assertFieldOutput(self, PhoneNumberField, valid_cases, invalid_cases)
