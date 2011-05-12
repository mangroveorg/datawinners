# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponse
from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import MangroveException
from mangrove.transport.submissions import SubmissionHandler, Request


def sms(request):
    _message = request.POST["message"]
    _from = request.POST["from_msisdn"]
    _to = request.POST["to_msisdn"]
    try:
        s = SubmissionHandler(dbm=get_db_manager())
        response = s.accept(Request(transport="sms", message=_message, source=_from, destination=_to))
        message = response.message
    except MangroveException as exception:
        message = exception.message
    return HttpResponse(message)
