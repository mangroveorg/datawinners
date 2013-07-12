from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datawinners import utils
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.accountmanagement.views import is_api_user
from datawinners.feeds.authorization import httpbasic, view_or_basicauth
from datawinners.scheduler.smsclient import SMSClient


def authenticate_api_user(username, password):
    user = authenticate(username=username, password=password)
    if is_api_user(user):
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
    number = request.POST["number"]
    message = request.POST["message"]
    organization = utils.get_organization(request)
    organization_setting = OrganizationSetting.objects.get(organization=organization)
    organization_tel_number = organization_setting.get_organisation_sms_number()[0]
    if SMSClient().send_sms(organization_tel_number, number, message):
        status="success"
    else:
        status="error"
    return HttpResponse('{"status":"%s"}'%status, content_type="application/javascript")