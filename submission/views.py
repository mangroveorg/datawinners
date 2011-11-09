# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
from django.http import HttpResponse
from django.utils import translation
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from datawinners.accountmanagement.models import OrganizationSetting, Organization, TEST_REPORTER_MOBILE_NUMBER
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_db_manager_for, get_organization_settings_for, get_database_manager
from datawinners.messageprovider.messages import exception_messages, SMS
from datawinners.ordersmsparser.order_sms_parser import OrderSMSParser
from datawinners.submission.models import DatawinnerLog, SMSResponse
from mangrove.errors.MangroveException import MangroveException, SubmissionParseException, FormModelDoesNotExistsException, NumberNotRegisteredException, DataObjectNotFound, UnknownOrganization, SMSParserInvalidFormatException, MultipleSubmissionsForSameCodeException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.player.parser import SMSParser
from mangrove.transport.player.player import SMSPlayer, Request, TransportInfo
from datawinners.messageprovider.message_handler import get_exception_message_for

import logging
logger = logging.getLogger("django")

def _test_mode_numbers(request):
    profile = request.user.get_profile()
    organization = Organization.objects.get(org_id=profile.org_id)
    organization_settings = OrganizationSetting.objects.get(organization=organization)
    _to = organization_settings.get_organisation_sms_number()
    _from = TEST_REPORTER_MOBILE_NUMBER
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
#TODO This needs some major refactoring. It is very clear that I want to do things which the accept method of the player outside the accept method and hence I am duplicating here.
def sms(request):
    _message = request.POST["message"]
    _from, _to = _get_from_and_to_numbers(request)
    if _to is None:
        return HttpResponse(_("Your organization does not have a telephone number assigned. Please contact DataWinners Support."))
    try:
        org_settings = get_organization_settings_for(_from, _to, request.user)
    except UnknownOrganization as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        log = DatawinnerLog(message=_message, from_number=_from, to_number=_to, error=message)
        log.save()
        return HttpResponse(message)

    if _from == TEST_REPORTER_MOBILE_NUMBER:
        get_database_manager(request.user)
    else:
        org_settings.increment_incoming_message_count()
        if not org_settings.should_handle_message():
            return HttpResponse(_("You have used up your 100 SMS for the trial account. Please upgrade to a monthly subscription to continue sending in data to your projects."))
        dbm = get_db_manager_for(_from, _to)

    try:
        if settings.USE_ORDERED_SMS_PARSER:
            sms_parser = OrderSMSParser(dbm)
        else:
            sms_parser = SMSParser()
        form_code, token = sms_parser.form_code(_message)
        form_model = get_form_model_by_code(dbm, form_code)
        translation.activate(form_model.activeLanguages[0])
    except (SubmissionParseException,SMSParserInvalidFormatException,MultipleSubmissionsForSameCodeException) as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        log = DatawinnerLog(message=_message, from_number=_from, to_number=_to, error=message)
        log.save()
        org_settings.increment_outgoing_message_count()
        return HttpResponse(message)
    except FormModelDoesNotExistsException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        log = DatawinnerLog(message=_message, from_number=_from, to_number=_to, form_code=exception.data[0],
                            error=message)
        log.save()
        org_settings.increment_outgoing_message_count()
        return HttpResponse(message)

    try:
        sms_player = SMSPlayer(dbm, get_location_tree(), sms_parser)
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
        log = DatawinnerLog(message=_message, from_number=_from, to_number=_to, error=message)
        log.save()
    except DataObjectNotFound as exception:
        message = exception_messages.get(DataObjectNotFound).get(SMS)
        message = message % (form_model.entity_type[0], exception.data[1], form_model.entity_type[0])
    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
    except Exception as exception:
        logger.exception('SMS Processing failure: message')
        message = get_exception_message_for(exception=exception, channel=SMS)

    org_settings.increment_outgoing_message_count()
    return HttpResponse(message)


