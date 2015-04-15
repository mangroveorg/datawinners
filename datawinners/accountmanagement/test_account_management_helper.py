from unittest import TestCase

from mock import patch

from datawinners.accountmanagement.helper import validate_email_addresses


class TestAccountManagementHelper(TestCase):
    def test_should_not_give_error_for_normal_case(self):
        reporter_details = {'rep1': 'some_email'}
        with patch("datawinners.accountmanagement.helper.datasender_count_with") as mock_datasender_count_with:
            mock_datasender_count_with.return_value = 0
            content, duplicate_entries, errors = validate_email_addresses(reporter_details)
        self.assertEqual(content, '')
        self.assertEqual(duplicate_entries, {})
        self.assertEqual(errors, [])

    def test_should_give_error_if_email_already_exists(self):
        reporter_details = {'rep1': 'some_email'}
        with patch("datawinners.accountmanagement.helper.datasender_count_with") as mock_datasender_count_with:
            mock_datasender_count_with.return_value = 1
            content, duplicate_entries, errors = validate_email_addresses(reporter_details)
        self.assertEqual(content,
                         '{"errors": ["User with email some_email already exists"], "success": false, "duplicate_entries": {}}')
        self.assertDictEqual(duplicate_entries, {})
        self.assertListEqual(errors, ['User with email some_email already exists'])

    def test_should_give_error_if_duplicate_entry_present(self):
        reporter_details = {'rep1': 'some_email', 'rep2': 'some_email'}
        with patch("datawinners.accountmanagement.helper.datasender_count_with") as mock_datasender_count_with:
            mock_datasender_count_with.return_value = 0
            content, duplicate_entries, errors = validate_email_addresses(reporter_details)
        self.assertEqual(content,
                         '{"errors": [], "success": false, "duplicate_entries": {"rep2": "some_email", "rep1": "some_email"}}')
        self.assertDictEqual(duplicate_entries, {'rep1': 'some_email', 'rep2': 'some_email'})
        self.assertListEqual(errors, [])