# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from messageprovider.handlers import exception_handlers, default_exception_handler

def handle(exception, request):
    handler = exception_handlers.get(type(exception), default_exception_handler)
    return handler(exception, request)
