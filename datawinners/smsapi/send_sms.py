from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import jsonpickle
from datawinners.common.authorization import api_http_basic
from datawinners.utils import get_organization
from datawinners.scheduler.smsclient import SMSClient


@csrf_exempt
@api_http_basic
def send_sms(request):
    input_request = jsonpickle.decode(request.raw_post_data)
    organization = get_organization(request)
    client = SMSClient()
    result = {}
    org_tel_number = organization.tel_number()
    for number in input_request['numbers']:
        if client.send_sms(org_tel_number, number, unicode(input_request['message'])):
            result.update({number: "success"})
            organization.increment_sms_api_usage_count()
        else:
            result.update({number: "failure"})
    return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type="application/javascript")
