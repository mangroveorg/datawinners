from django.utils.translation import ugettext as _
import re


def transform_error_message(message):
    if "Duplicate column header" in message:
        return get_duplicate_column_error(message)
    if "two survey elements named" in message:
        return get_duplicate_element_names_error_in_survey_sheet(message)
    return parse(message) + _(" Update your XLSForm and upload again.")


def get_duplicate_column_error(message):
    message = message.split(":")
    return _(message[0] + " %s") % message[1]


def escape_special_characters(pattern):
    special_chars = ['[', ']', '$', '^', '&', '*', '.', '\\', '?', '(', ')']
    original_pattern = pattern
    for char in original_pattern:
        if char in special_chars:
            char_pattern = "\\" + char
            pattern = re.sub(char_pattern, '\\' + char, pattern)
    return pattern


def replace_param_for_string_substitution(arguments, message):
    for pattern in arguments:
        pattern = escape_special_characters(pattern)
        message = re.sub(pattern, "%s", message)
    return message


def parse(message):
    arguments = re.findall("\[\D*\d*\]", message)
    if arguments:
        message = replace_param_for_string_substitution(arguments, message)
        return _(message) % tuple([pattern for pattern in arguments])
    return _(message)

def get_duplicate_element_names_error_in_survey_sheet(message):
    element_names = re.findall("\'(\w*)\'",message)
    if element_names:
        escaped_element_names = ['\''+name+'\'' for name in element_names]
        message = replace_param_for_string_substitution(escaped_element_names,message)
        return _(message) % element_names[0]
