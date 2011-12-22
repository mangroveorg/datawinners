# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils import translation
from mangrove.form_model.form_model import get_form_model_by_code
import mangrove.errors.MangroveException as ex
from messageprovider.message_handler import get_exception_message_for
from messageprovider.messages import SMS

def default_exception_handler(exception, request):
    return  get_exception_message_for(exception=exception, channel=SMS)

def default_exception_handler_with_logger(exception, request):
    response = request['datawinner_log'].error = get_exception_message_for(exception=exception, channel=SMS)
    request['datawinner_log'].save()
    return response

def data_object_not_found_handler(exception, request):
    return get_exception_message_for(exception=exception, channel=SMS, formatter=data_object_not_found_formatter)

def sms_parser_wrong_number_of_answers_handler(exception, request):
    _activate_language(exception, request)
    return default_exception_handler_with_logger(exception, request)

exception_handlers = {

    ex.DataObjectNotFound : data_object_not_found_handler,
    ex.FormModelDoesNotExistsException : default_exception_handler_with_logger,
    ex.NumberNotRegisteredException : default_exception_handler_with_logger,
    ex.SubmissionParseException : default_exception_handler_with_logger,
    ex.SMSParserInvalidFormatException : default_exception_handler_with_logger,
    ex.MultipleSubmissionsForSameCodeException : default_exception_handler_with_logger,
    ex.SMSParserWrongNumberOfAnswersException : sms_parser_wrong_number_of_answers_handler,
}

def data_object_not_found_formatter(data_object_not_found_exception, message):
    entity_type, param, value = data_object_not_found_exception.data
    return message % (entity_type,value,entity_type)

def _activate_language(exception, request):
    form_model = get_form_model_by_code(request['dbm'], exception.data[0])
    translation.activate(form_model.activeLanguages[0])

