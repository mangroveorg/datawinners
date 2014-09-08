from django.utils.translation import ugettext as _
import re


def transform_error_message(message):
    if "Duplicate column header" in message:
        return get_duplicate_column_error(message)
    elif "[row :" in message:
        return get_error_message_with_row_number(message)

def get_duplicate_column_error(message):
    message = message.split(":")
    return _(message[0] + " %s") % message[1]

def get_error_message_with_row_number(message):
    row_info_patterns = re.findall("\[\D*\d*\]",message)
    if row_info_patterns:
        for pattern in row_info_patterns:
            pattern = escape_special_characters(pattern)
            message = re.sub(pattern,"%s",message)
        return _(message) % tuple([pattern for pattern in row_info_patterns])


def escape_special_characters(pattern):
    special_chars = ['[',']','$','^' ,'&','*','.','\\','?','(',')']
    original_pattern = pattern
    for char in original_pattern:
        if char in special_chars:
            char_pattern = "\\" +char
            pattern = re.sub(char_pattern ,'\\'+char,pattern)
    return pattern