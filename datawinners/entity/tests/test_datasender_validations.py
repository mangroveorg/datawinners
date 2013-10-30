import unittest
from datawinners.entity.datasender_validators import ShortCodeValidator


class TestDatasenderShortCodeValidator(unittest.TestCase):
    def setUp(self):
        self.short_code_validator = ShortCodeValidator()

    def test_should_not_allow_short_code_more_than_12_chars(self):
        expected_err_msg = "Unique ID should be less than 12 characters."

        error_list = self.short_code_validator.validate({'s': '1234567890123'})

        self.assertEquals(len(error_list), 1)
        self.assertEquals(error_list[0].message, expected_err_msg)

    def test_should_not_return_error_if_no_short_code_provided(self):
        result = self.short_code_validator.validate({'s':''})
        self.assertEqual(result, [])

    def test_should_not_allow_special_characters_in_short_code(self):
        expected_err_msg = "Only letters and numbers are valid."

        error_list = self.short_code_validator.validate({'s': 'abc@$%^&&*'})

        self.assertEquals(len(error_list), 1)
        self.assertEquals(error_list[0].message, expected_err_msg)
