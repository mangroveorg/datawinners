from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import jsonpickle
from datawinners.utils import get_organization
from datawinners.accountmanagement.views import is_sms_api_user
from datawinners.feeds.authorization import view_or_basicauth
from datawinners.scheduler.smsclient import SMSClient


def authenticate_api_user(username, password):
    user = authenticate(username=username, password=password)
    if is_sms_api_user(user):
        return user
    return None


def api_http_basic(view, realm="Datawinners"):
    def view_decorator(request, *args, **kwargs):
        return view_or_basicauth(view, request,
                                 lambda u: u.is_authenticated(),
                                 authenticate_api_user,
                                 realm, *args, **kwargs)

    return view_decorator


@csrf_exempt
@api_http_basic
def send_sms(request):
    input_request = jsonpickle.decode(request.raw_post_data)
    organization = get_organization(request)
    client = SMSClient()
    result = {}
    org_tel_number = organization.tel_number()
    for number in input_request['numbers']:
        if client.send_sms(org_tel_number, number, input_request['message']):
            result.update({number: "success"})
            organization.increment_sms_api_usage_count()
        else:
            result.update({number: "failure"})
    return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type="application/javascript")
