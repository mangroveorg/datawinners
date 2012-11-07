# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils.translation import ugettext as _
from mangrove.errors.MangroveException import MangroveException
from mangrove.form_model.form_model import  get_form_model_by_code
from mangrove.utils.types import is_empty
from datawinners.messageprovider.messages import exception_messages, DEFAULT, get_submission_success_message, get_registration_success_message, get_validation_failure_error_message
from datawinners.messageprovider.message_builder import ResponseBuilder


def default_formatter(exception, message):
    if isinstance(exception, MangroveException) and exception.data is not None and "%s" in message:
        return message % exception.data
    return message


def get_exception_message_for(exception, channel=None, formatter=default_formatter):
    ex_type = type(exception)
    if channel is not None:
        message_dict = exception_messages.get(ex_type)
        if message_dict is None:
            return exception.message
        message = message_dict.get(channel)
        if is_empty(message):
            message = exception_messages[ex_type].get(DEFAULT)
        message = _(message)
    else:
        message = exception_messages[ex_type][DEFAULT]
        message = _(message)
    return formatter(exception, message)


def get_submission_error_message_for(errors):
# :-( :-( :-(
    if isinstance(errors, dict):
        error_message = get_validation_failure_error_message() % ", ".join(errors.keys())
    else:
        error_message = errors
    return error_message


def get_success_msg_for_submission_using(response, form_model):
    message = get_submission_success_message()
    response_text = ResponseBuilder(form_model=form_model, processed_data=response.processed_data).get_expanded_response()
    message_with_response_text = message + " " + response_text

    return message_with_response_text if len(message_with_response_text) <= 160 else message


def get_success_msg_for_registration_using(response, source, form_model=None):
    resp_string = (_("ID is:") + " %s") % (response.short_code,)

    thanks = get_registration_success_message() % resp_string
    if source == "sms":
        return thanks + ResponseBuilder(form_model=form_model, processed_data=response.processed_data).get_expanded_response()
    return thanks


def _get_response_message(response, dbm):
    if response.success:
        form_model = get_form_model_by_code(dbm, response.form_code)
        message = _get_success_message(response, form_model)
    else:
        message = get_submission_error_message_for(response.errors)
    return message


def _get_success_message(response, form_model):
    if response.is_registration:
        return get_success_msg_for_registration_using(response, "sms", form_model)
    else:
        return get_success_msg_for_submission_using(response, form_model)