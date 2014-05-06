# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import translation
from mangrove.form_model.form_model import get_form_model_by_code, FORM_CODE
import mangrove.errors.MangroveException as ex
from datawinners.messageprovider.message_handler import get_exception_message_for
from datawinners.messageprovider.messages import SMS
from datawinners.submission.models import DatawinnerLog

def default_exception_handler(exception, request):
    return  get_exception_message_for(exception=exception, channel=SMS)

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
    _activate_language(exception, request)
    return default_exception_handler_with_logger(exception, request)

def exceed_limit_handler(exception, request):
    request.get('organization').increment_message_count_for(sms_registration_count=1)
    return default_exception_handler_with_logger(exception, request)
    

exception_handlers = {

    ex.DataObjectNotFound : data_object_not_found_handler,
    ex.FormModelDoesNotExistsException : wrong_questionnaire_code_handler,
    ex.NumberNotRegisteredException : default_exception_handler_with_logger,
    ex.SubmissionParseException : default_exception_handler_with_logger,
    ex.SMSParserInvalidFormatException : default_exception_handler_with_logger,
    ex.MultipleSubmissionsForSameCodeException : default_exception_handler_with_logger,
    ex.SMSParserWrongNumberOfAnswersException : sms_parser_wrong_number_of_answers_handler,
    ex.ExceedSMSLimitException : exceed_limit_handler,
    ex.ExceedSubmissionLimitException : exceed_limit_handler,
}

def data_object_not_found_formatter(data_object_not_found_exception, message):
    entity_type, param, value = data_object_not_found_exception.data
    return message % (entity_type.capitalize(),value)

def create_failure_log(error_message, request):
    log = DatawinnerLog()
    log.error = error_message
    log.form_code = request.get(FORM_CODE,'')
    log.message = request.get('incoming_message')
    log.from_number = request['transport_info'].source
    log.to_number = request['transport_info'].destination
    log.organization = request.get('organization')
    log.save()

def _activate_language(exception, request):
    form_model = get_form_model_by_code(request['dbm'], exception.data[0])
    translation.activate(form_model.activeLanguages[0])

