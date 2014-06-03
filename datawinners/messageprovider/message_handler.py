# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from string import lower
from django.utils.translation import ugettext as _
from mangrove.errors.MangroveException import MangroveException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from mangrove.utils.types import is_empty
from datawinners.messageprovider.messages import exception_messages, DEFAULT, get_submission_success_message, get_registration_success_message, get_validation_failure_error_message, get_subject_info
from datawinners.messageprovider.message_builder import ResponseBuilder


def default_formatter(exception, message):
    if isinstance(exception, MangroveException) and exception.data is not None and "%s" in message:
        formatted_message = message % exception.data
        return formatted_message if len(formatted_message) <= 160 else message.replace('%s', "")
    return message

def data_object_not_found_formatter(exception, message):
    return message % (exception.data[1])

def data_object_not_found_formatter(exception, message):
    return message % (exception.data[1])


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


def get_submission_error_message_for(response, form_model, dbm, request):
    from datawinners.messageprovider.handlers import unique_id_not_registered_handler, invalid_answer_handler

    errors = response.errors
    if isinstance(errors, dict) and form_model:

        is_unique_id_error_present, unique_id_type, invalid_unique_id_code = _is_unique_id_not_present_error(errors)
        if is_unique_id_error_present:
            return unique_id_not_registered_handler(dbm, form_model.form_code, invalid_unique_id_code, request)

        keys = [_("question_prefix%s") % index_of_question(form_model, question_code) for question_code in
                errors.keys()]
        keys.sort()
        if len(keys) == 1:
            error_text = keys[0]
        else:
            and_msg = "ending_and" if len(keys) >= 3 else "and"
            if len(keys) <= 3:
                error_text = "%s %s %s" % (
                    _("sms_glue").join(keys[:-1]), _(and_msg), keys[-1])
            else:
                error_text = "%s %s %s" % (
                    _("sms_glue").join(keys[:3]), _(and_msg), _("more_wrong_question"))
        error_message = invalid_answer_handler(dbm, request, form_model.form_code, error_text)
    else:
        error_message = errors
    return error_message


def get_success_msg_for_submission_using(response, form_model, dbm, request):
    from datawinners.messageprovider.handlers import success_questionnaire_submission_handler
    datasender_name = response.reporters[0].get('name').split()[0].capitalize()
    answers_response_text = ResponseBuilder(form_model=form_model,
                                    processed_data=response.processed_data).get_expanded_response()
    message = success_questionnaire_submission_handler(dbm, form_model.form_code, datasender_name, answers_response_text, request)

    return message


def get_success_msg_for_ds_registration_using(response, source, form_model=None):
    thanks = get_registration_success_message(response)
    if source == "sms":
        message_with_response_text = thanks + " " + ResponseBuilder(form_model=form_model,
                                                                    processed_data=response.processed_data).get_expanded_response()
        return message_with_response_text if len(
            message_with_response_text) <= 160 else thanks + " " + get_subject_info(response, form_model)
    return _("Registration successful.") + " %s %s" % (_("ID is:"), response.short_code)

def get_success_msg_for_subject_registration_using(dbm,response,form_model=None):
    from datawinners.messageprovider.handlers import success_subject_registration_handler
    datasender_name = response.reporters[0].get('name').split()[0].capitalize()
    answers_response_text = ResponseBuilder(form_model=form_model,
                                    processed_data=response.processed_data).get_response_for_sms_subject_registration()
    message = success_subject_registration_handler(dbm, datasender_name, answers_response_text)

    return message


def get_response_message(response, dbm, request):
    form_model = get_form_model_by_code(dbm, response.form_code) if response.form_code else None
    if response.success:
        message = _get_success_message(response, form_model, dbm, request)
    else:
        message = get_submission_error_message_for(response, form_model, dbm, request)
    return message


def _get_success_message(response, form_model, dbm, request):
    if response.is_registration:
        if response.entity_type == REPORTER_ENTITY_TYPE:
            return get_success_msg_for_ds_registration_using(response,'sms', form_model)
        else:
            return get_success_msg_for_subject_registration_using(dbm,response,form_model)
    else:
        return get_success_msg_for_submission_using(response, form_model, dbm, request)
