import unittest
from datawinners.blue.error_translation_utils import transform_error_message

EXPECTED_DUPLICATE_HEADER_ERROR = "Duplicate column header: 'column_name'. Update your XLSForm and upload again."
EXPECTED_DUPLICATE_ELEMENT_NAME_ERROR = "There are two survey elements named 'ff'. Update your XLSForm and upload again."
EXPECTED_LIST_NAME_NOT_IN_CHOICES_SHEET_ERROR = "[row : 2] List name not in choices sheet: list. Update your XLSForm and upload again."
EXPECTED_UNMATCHED_BEGIN_STATEMENT_ERROR = "Unmatched begin statement: repeat. Update your XLSForm and upload again."
EXPECTED_SPACE_NOT_ALLOWED_IN_CHOICES_ERROR = "Choice names with spaces cannot be added to multiple choice selects. See [spaced name] in [list]. Update your XLSForm and upload again."

class TestErrorTranslationUtils(unittest.TestCase):

    def test_error_message_for_duplicate_column_header(self):
        error_message = transform_error_message("Duplicate column header:column_name")
        self.assertEquals(error_message,EXPECTED_DUPLICATE_HEADER_ERROR)

    def test_error_message_for_duplicate_element_names(self):
        error_message = transform_error_message("There are two survey elements named 'ff' in the section named 'tmpgCbbjT'.")
        self.assertEquals(error_message,EXPECTED_DUPLICATE_ELEMENT_NAME_ERROR)

    def test_error_message_list_name_not_in_choices_sheet(self):
        error_message = transform_error_message('[row : 2] List name not in choices sheet: list')
        self.assertEquals(error_message,EXPECTED_LIST_NAME_NOT_IN_CHOICES_SHEET_ERROR)

    def test_error_message_for_unmatched_begin_statement(self):
        error_message = transform_error_message('Unmatched begin statement: repeat')
        self.assertEquals(error_message,EXPECTED_UNMATCHED_BEGIN_STATEMENT_ERROR)

    def test_error_message_for_spaces_in_choices_name_for_multiple_select_choices(self):
        error_message = transform_error_message('Choice names with spaces cannot be added to multiple choice selects. See [spaced name] in [list]')
        self.assertEquals(error_message,EXPECTED_SPACE_NOT_ALLOWED_IN_CHOICES_ERROR)

