# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from string import strip
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import MangroveException
from mangrove.transport.submissions import SubmissionHandler, Request


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
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


def _get_data(post, key):
    if post.get(key):
        return post.get(key)
    return None


def _get_submission(post):
    format = post.get('format')
    data = json.loads(post.get('data'))
    return {
            'transport': _get_data(data, 'transport'),
            'source': _get_data(data, 'source'),
            'destination': _get_data(data, 'destination'),
            'message': _get_data(data, 'message')
           }


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def submit(request):
    post = _get_submission(request.POST)
    message = ''
    success = True
    try:
        s = SubmissionHandler(dbm=get_db_manager())
        request = Request(transport=post.get('transport'), message=post.get('message'), source=post.get('source'),
                          destination=post.get('destination'))
        response = s.accept(request)
        message = response.message
    except MangroveException as exception:
        message = exception.message
        success = False
    return HttpResponse(json.dumps({'success': success, 'message' : message, 'entity_id': response.datarecord_id}))
