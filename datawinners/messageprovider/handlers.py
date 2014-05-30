# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.form_model.form_model import FORM_CODE
import mangrove.errors.MangroveException as ex

from datawinners.messageprovider.customized_message import get_customized_message_for_questionnaire, get_account_wide_sms_reply
from datawinners.submission.models import DatawinnerLog
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import SMS


def default_exception_handler(exception, request):
    return get_exception_message_for(exception=exception, channel=SMS)


def default_exception_handler_with_logger(exception, request):
    exception_message = get_exception_message_for(exception=exception, channel=SMS)
    create_failure_log(exception_message, request)
    return exception_message

def wrong_questionnaire_code_handler(exception, request):
    if request.get('exception'):
        handler = exception_handlers.get(type(request.get('exception')), default_exception_handler)
        return handler(request.get('exception'), request)
    return default_exception_handler_with_logger(exception, request)

def data_object_not_found_handler(exception, request):
    return get_exception_message_for(exception=exception, channel=SMS, formatter=data_object_not_found_formatter)


def sms_parser_wrong_number_of_answers_handler(exception, request):
    return default_exception_handler_with_logger(exception, request)

def exceed_limit_handler(exception, request):
    request.get('organization').increment_message_count_for(sms_registration_count=1)
    return default_exception_handler(exception, request)

def number_not_registered_exception_handler(exception, request):
    handler = default_exception_handler if request.get('is_registration') else default_exception_handler_with_logger
    return handler(exception, request)


def unique_id_not_registered_handler(dbm, form_code, invalid_unique_id_code):
    return get_customized_message_for_questionnaire(dbm, None, "reply_identification_number_not_registered",
                                                            form_code, placeholder_dict=
                                                            {'Submitted Identification Number': invalid_unique_id_code})

def incorrect_number_of_answers(dbm, form_code, request):
    message = get_customized_message_for_questionnaire(dbm, request, "reply_incorrect_number_of_responses",
                                                             form_code)
    create_failure_log(message, request)
    return message

def invalid_answer_handler(dbm, request, form_code, invalid_answers):
    return get_customized_message_for_questionnaire(dbm, request, "reply_incorrect_answers",
                                                            form_code, placeholder_dict=
                                                            {'Question Numbers for Wrong Answer(s)': invalid_answers})

def incorrect_questionnaire_code(dbm, invalid_form_code):
    return get_account_wide_sms_reply(dbm, "reply_incorrect_questionnaire_code",
                                                            placeholder_dict=
                                                            {'Submitted Questionnaire Code': invalid_form_code})

def identification_number_already_exists(dbm, submitted_id,identification_number_type):
    return get_account_wide_sms_reply(dbm, "reply_identification_number_already_exists",
                                                            placeholder_dict=
                                                            {'Submitted Identification Number': submitted_id,
                                                             'Identification Number Type':identification_number_type})

def sms_parser_invalid_format_handler(exception, request):
    if len(request.get('incoming_message').strip().split()) != 1:
        return default_exception_handler_with_logger(exception, request)

    #_activate_language(exception, request)
    message = get_customized_message_for_questionnaire(request['dbm'], request,
                                                             message_code='reply_incorrect_number_of_responses',
                                                             form_code=exception.data[0][0])
    create_failure_log(message, request)
    return message
# def sms_parser_invalid_format_handler(exception, request):
#     if len(request.get('incoming_message').strip().split()) != 1:
#         return default_exception_handler_with_logger(exception, request)
#
#     _activate_language(exception, request)
#     new_exception = ex.SMSParserWrongNumberOfAnswersException(exception.data[0][0])
#     return default_exception_handler_with_logger(new_exception, request)


def data_sender_not_linked_handler(dbm, request, form_code):
    message = get_customized_message_for_questionnaire(dbm, request,
                                                             message_code='reply_ds_not_authorized',
                                                             form_code=form_code)
    create_failure_log(message, request)

    return message

def data_sender_not_registered_handler(dbm):
    message = get_account_wide_sms_reply(dbm, message_code='reply_ds_not_registered')
    return message


def success_questionnaire_submission_handler(dbm, form_code, datasender_name, list_of_answers):

    message = get_customized_message_for_questionnaire(dbm, None,
                                                             message_code='reply_success_submission',
                                                             form_code=form_code, placeholder_dict= {
                                                            'Name of Data Sender': datasender_name,
                                                            'List of Answers': list_of_answers
                                                            })
    if len(message) > 160:
        message = get_customized_message_for_questionnaire(dbm, None,
                                                            message_code="reply_success_submission",
                                                            form_code=form_code, placeholder_dict= {
                                                            'Name of Data Sender': datasender_name,
                                                            'List of Answers': ''
                                                            })
        message = message.rstrip(': ') + "."

    return message

def success_subject_registration_handler(dbm, datasender_name, list_of_answers):

    message = get_account_wide_sms_reply(dbm,  message_code='reply_success_identification_number_registration',
                                         placeholder_dict= { 'Name of Data Sender': datasender_name, 'Identification Number Type': list_of_answers[0],
                                                             'Name of Identification Number':list_of_answers[1],'Submitted Identification Number':list_of_answers[2]})
    return message

exception_handlers = {

    ex.DataObjectNotFound: data_object_not_found_handler,
    ex.FormModelDoesNotExistsException: wrong_questionnaire_code_handler,
    ex.NumberNotRegisteredException: number_not_registered_exception_handler,
    ex.SubmissionParseException: default_exception_handler_with_logger,
    ex.SMSParserInvalidFormatException: sms_parser_invalid_format_handler,
    ex.MultipleSubmissionsForSameCodeException: default_exception_handler_with_logger,
    ex.SMSParserWrongNumberOfAnswersException: default_exception_handler_with_logger,
    ex.ExceedSMSLimitException: exceed_limit_handler,
    ex.ExceedSubmissionLimitException: exceed_limit_handler,
    ex.DatasenderIsNotLinkedException: default_exception_handler_with_logger,

    }




def data_object_not_found_formatter(data_object_not_found_exception, message):
    entity_type, param, value = data_object_not_found_exception.data
    return message % value

def create_failure_log(error_message, request):
    log = DatawinnerLog()
    log.error = error_message
    log.form_code = request.get(FORM_CODE,'')
    log.message = request.get('incoming_message')
    log.from_number = request['transport_info'].source
    log.to_number = request['transport_info'].destination
    log.organization = request.get('organization')
    log.save()
