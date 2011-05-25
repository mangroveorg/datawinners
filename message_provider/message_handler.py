# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.utils.types import is_empty
from message_provider.messages import messages, DEFAULT, DEFAULT_EXCEPTION_MESSAGE

def get_exception_message_for(type, channel=None, code=None):
    if channel is not None:
        message_dict = messages.get(type)
        if message_dict is None:
            return DEFAULT_EXCEPTION_MESSAGE
        message = message_dict.get(channel)
        if is_empty(message):
            message = messages[type].get(DEFAULT)
    else:
        message = messages[type][DEFAULT]
    if code is not None and "%s" in message:
        return message % code
    return message