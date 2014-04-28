# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from string import lower
from django.utils.translation import ugettext as _
from mangrove.errors.MangroveException import MangroveException, DataObjectNotFound
from mangrove.form_model.form_model import  get_form_model_by_code
from mangrove.utils.types import is_empty
from datawinners.messageprovider.messages import exception_messages, DEFAULT, get_submission_success_message, get_registration_success_message, get_validation_failure_error_message, get_subject_info
from datawinners.messageprovider.message_builder import ResponseBuilder


def default_formatter(exception, message):
    if isinstance(exception, MangroveException) and exception.data is not None and "%s" in message:
        formatted_message = message % exception.data
        return formatted_message if len(formatted_message) <= 160 else message.replace('%s', "")
    return message


def get_exception_message_for(exception, channel=None, formatter=default_formatter):
    ex_type = type(exception)
    if channel is not None:
        message_dict = exception_messages.get(ex_type)
        if message_dict is None:
            return _(exception.message)
        message = message_dict.get(channel)
        if is_empty(message):
            message = exception_messages[ex_type].get(DEFAULT)
        message = _(message)
    else:
        message = exception_messages[ex_type][DEFAULT]
        message = _(message)
    return formatter(exception, message)

def index_of_question(form_model, question_code):
    return [index for index, field in enumerate(form_model.fields) if field.code.lower() == lower(question_code)][0] + 1


def _is_unique_id_not_present_error(errors):
    for error in errors.values():
        re_match = re.match(r"([A-Za-z0-9 ]+) with Unique Identification Number \(ID\) = ([^\s]+) not found", error)
        if re_match:
            return True, re_match.group(1), re_match.group(2)
    return False, None, None


def _get_error_message(keys, response):
    error = response.errors.values()[0]
    error_text = "%s %s" % (_("singular_question"), keys[0])
    return get_validation_failure_error_message(response) % error_text.strip()


def get_submission_error_message_for(response, form_model):
    errors = response.errors
    if isinstance(errors, dict) and form_model:

        is_unique_id_error_present, unique_id_type, invalid_unique_id_code = _is_unique_id_not_present_error(errors)
        if is_unique_id_error_present:
            return get_exception_message_for(
                DataObjectNotFound(unique_id_type, invalid_unique_id_code, unique_id_type),
                channel='sms')


        keys = [_("question_prefix%s") % index_of_question(form_model, question_code) for question_code in errors.keys()]
        keys.sort()
        if len(keys) == 1:
            error_message = _get_error_message(keys, response)
        else:
            and_msg = "ending_and" if len(keys) >= 3 else "and"
            errors_text = "%s %s %s %s" % (_("plural_question"), _("sms_glue").join(keys[:-1]),  _(and_msg), keys[-1])
            error_message = get_validation_failure_error_message(response) % errors_text.strip()
    else:
        error_message = errors
    return error_message


def get_success_msg_for_submission_using(response, form_model):
    message = get_submission_success_message(response)
    response_text = ResponseBuilder(form_model=form_model, processed_data=response.processed_data).get_expanded_response()
    message_with_response_text = message + ": " + response_text

    return message_with_response_text if len(message_with_response_text) <= 160 else message + "."


def get_success_msg_for_registration_using(response, source, form_model=None):
    thanks = get_registration_success_message(response)
    if source == "sms":
        message_with_response_text = thanks + ": " + ResponseBuilder(form_model=form_model, processed_data=response.processed_data).get_expanded_response()
        return message_with_response_text if len(message_with_response_text) <= 160 else thanks + " " + get_subject_info(response, form_model)
    return _("Registration successful.") + " %s %s" %  (_("ID is:"), response.short_code)


def _get_response_message(response, dbm):

    form_model = get_form_model_by_code(dbm, response.form_code) if response.form_code else None
    if response.success:
        message = _get_success_message(response, form_model)
    else:
        message = get_submission_error_message_for(response, form_model)
    return message


def _get_success_message(response, form_model):
    if response.is_registration:
        return get_success_msg_for_registration_using(response, "sms", form_model)
    else:
        return get_success_msg_for_submission_using(response, form_model)