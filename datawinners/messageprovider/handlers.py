# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import translation
from mangrove.form_model.form_model import get_form_model_by_code, FORM_CODE, EntityFormModel
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
    return default_exception_handler_with_logger(exception, request)

def exceed_limit_handler(exception, request):
    request.get('organization').increment_message_count_for(sms_registration_count=1)
    return default_exception_handler(exception, request)
    
def number_not_registered_exception_handler(exception, request):
    handler = default_exception_handler if request.get('is_registration') else default_exception_handler_with_logger
    return handler(exception, request)

def sms_parser_invalid_format_handler(exception, request):
    new_exception = _activate_language_and_update_exception(exception, request)
    return default_exception_handler_with_logger(new_exception, request)

exception_handlers = {

    ex.DataObjectNotFound : data_object_not_found_handler,
    ex.FormModelDoesNotExistsException : wrong_questionnaire_code_handler,
    ex.NumberNotRegisteredException : number_not_registered_exception_handler,
    ex.SubmissionParseException : default_exception_handler_with_logger,
    ex.SMSParserInvalidFormatException : sms_parser_invalid_format_handler,
    ex.MultipleSubmissionsForSameCodeException : default_exception_handler_with_logger,
    ex.SMSParserWrongNumberOfAnswersException : sms_parser_wrong_number_of_answers_handler,
    ex.ExceedSMSLimitException : exceed_limit_handler,
    ex.ExceedSubmissionLimitException : exceed_limit_handler,
    ex.DatasenderIsNotLinkedException : default_exception_handler_with_logger,
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

def _activate_language_and_update_exception(exception, request):
    try:
        form_model = get_form_model_by_code(request['dbm'], exception.data[0][0])
        language = request.get('organization').language if isinstance(form_model, EntityFormModel) else form_model.activeLanguages[0]
        new_exception = ex.SMSParserWrongNumberOfAnswersException(exception.data[0][0])
    except ex.FormModelDoesNotExistsException as exception:
        language = request.get('organization').language
        new_exception = exception

    translation.activate(language)
    return new_exception