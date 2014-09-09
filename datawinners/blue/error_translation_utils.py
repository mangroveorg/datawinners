from django.utils.translation import ugettext as _
import re


def transform_error_message(message):
    if not message:
        return ""
    if "Duplicate column header" in message:
        message = get_duplicate_column_error(message)
    elif "two survey elements named" in message:
        message = get_duplicate_element_names_error_in_survey_sheet(message)
    elif "List name not in choices" in message or "Unmatched begin statement" in message:
        pattern = "\[\D*\d*\]|:\s\d*\D*"
        message = parse(message,pattern)
    else:
        message = parse(message)
    return message + _(" Update your XLSForm and upload again.")


def get_duplicate_column_error(message):
    message = message.split(":")
    return _(message[0] + " %s") % message[1]


def escape_special_characters(pattern):
    special_chars = ['[', ']', '$', '^', '&', '*', '.', '\\', '?', '(', ')']
    original_pattern = pattern
    for char in special_chars:
        if char in original_pattern:
            char_pattern = "\\" + char
            pattern = re.sub(char_pattern, '\\' + char, pattern)
    return pattern

def replace_param_for_string_substitution(arguments, message):
    for pattern in arguments:
        pattern = escape_special_characters(pattern)
        message = re.sub(pattern, "%s", message)
    return message


def parse(message, pattern=None):
    matching_pattern = pattern or "\[([^\]\[]+)\]" #matches anything between []
    arguments = re.findall(matching_pattern, message)
    if arguments:
        message = replace_param_for_string_substitution(arguments, message)
        return _(message) % tuple([pattern for pattern in arguments])
    return _(message)


def get_duplicate_element_names_error_in_survey_sheet(message):
    element_names = re.findall("\'(\w*)\'", message)
    if element_names:
        escaped_element_names = ['\'' + name + '\'' for name in element_names]
        message = replace_param_for_string_substitution(escaped_element_names, message)
        return _(message) % element_names[0]

def translate_odk_message(message):
   if "Group has no children" in message:
        return _("No content in Group.")
   return message
