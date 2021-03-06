from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import jsonpickle
from datawinners.common.authorization import api_http_basic
from datawinners.sms.models import MSG_TYPE_API
from datawinners.utils import get_organization
from datawinners.scheduler.smsclient import SMSClient
from django.conf import settings
import datetime


NUMBERS = 'numbers'
MESSAGE = 'message'

@csrf_exempt
@api_http_basic
def send_sms(request):

    try:
        input_request = jsonpickle.decode(request.raw_post_data)
        if not (input_request.get(NUMBERS) and input_request.get(MESSAGE)):
            raise ValueError
    except ValueError:
        return HttpResponse(status=400)

    organization = get_organization(request)
    current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
    message_tracker = organization._get_message_tracker(current_month)
    client = SMSClient()
    result = {}
    org_tel_number = organization.tel_number()
    for number in input_request[NUMBERS]:
        if client.send_sms(org_tel_number, number, unicode(input_request[MESSAGE]), MSG_TYPE_API, message_tracker):
            result.update({number: "success"})
        else:
            result.update({number: "failure"})
    return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type="application/javascript")
