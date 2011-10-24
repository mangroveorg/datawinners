from django.test.testcases import TestCase
from datawinners.entity.fields import PhoneNumberField, EMPTY_VALUES
from datawinners.tests.backport import assertFieldOutput


class TestPhoneNumberField(TestCase):
    def test_should_validate_and_clean_phone_numbers(self):
        valid_cases = {
            '1112223333': '1112223333',
            '111-222-3333': '1112223333',
            '650-636-8600': '6506368600',
            "6-50636-8600": "6506368600",
            }
        invalid_cases = {
            'a': ['Please enter a valid phone number.Only numbers and -(dash) allowed'],
            '650 636 8600': ['Please enter a valid phone number.Only numbers and -(dash) allowed'],
            '(650)6368600': ['Please enter a valid phone number.Only numbers and -(dash) allowed'],
            }
        assertFieldOutput(self, PhoneNumberField, valid_cases, invalid_cases)
