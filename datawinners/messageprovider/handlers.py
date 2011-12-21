# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils.translation import ugettext
import mangrove.errors.MangroveException as ex
from messageprovider.message_handler import get_exception_message_for
from messageprovider.messages import SMS

def default_exception_handler(exception, request):
    response = request['datawinner_log'].error = get_exception_message_for(exception=exception, channel=SMS)
    request['datawinner_log'].save()
    return response

def data_object_not_found_formatter(data_object_not_found_exception, message):
    entity_type, param, value = data_object_not_found_exception.data
    return message % (entity_type,value,entity_type)


def data_object_not_found_handler(exception, request):
    return get_exception_message_for(exception=exception, channel=SMS, formatter=data_object_not_found_formatter)

exception_handlers = {

    ex.DataObjectNotFound : data_object_not_found_handler

}

