# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from datawinners.accountmanagement.models import OrganizationSetting, Organization
from datawinners.initializer import TEST_REPORTER_MOBILE_NUMBER
from datawinners.location.LocationTree import LocationTree
from datawinners.main.utils import get_db_manager_for
from datawinners.submission.models import DatawinnerLog, SMSResponse
from mangrove.errors.MangroveException import MangroveException, SubmissionParseException, FormModelDoesNotExistsException, NumberNotRegisteredException
from mangrove.transport.player.player import SMSPlayer, Request, TransportInfo
from mangrove.transport.submissions import SubmissionHandler
from datawinners.messageprovider.message_handler import get_exception_message_for

SMS = "sms"
WEB = "web"

import logging
logger = logging.getLogger("django")

def _test_mode_numbers(request):
    profile = request.user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    _from = TEST_REPORTER_MOBILE_NUMBER
    organization_settings = OrganizationSetting.objects.get(organization=organization)
    _to = organization_settings.sms_tel_number
    return _from, _to


def _get_from_and_to_numbers(request):
    if request.POST.get('test_mode'):
        return _test_mode_numbers(request)

    _from = request.POST["from_msisdn"]
    _to = request.POST["to_msisdn"]
    return _from, _to


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def sms(request):
    _message = request.POST["message"]
    _from, _to = _get_from_and_to_numbers(request)
    try:
        dbm = get_db_manager_for(_to)
        sms_player = SMSPlayer(dbm, SubmissionHandler(dbm), LocationTree())
        transportInfo = TransportInfo(transport=SMS, source=_from, destination=_to)
        response = sms_player.accept(Request(transportInfo=transportInfo, message=_message))
        message = SMSResponse(response).text()

    except (SubmissionParseException, FormModelDoesNotExistsException,) as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        log = DatawinnerLog(message=_message, from_number=_from, to_number=_to, form_code=exception.data[0],
                            error=message)
        log.save()
    except NumberNotRegisteredException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        log = DatawinnerLog(message=_message, from_number=_from, to_number=_to, form_code=None, error=message)
        log.save()
    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
    except Exception as exception:
        logger.exception('SMS Processing failure: message')
        message = get_exception_message_for(exception=exception, channel=SMS)

    return HttpResponse(message)


