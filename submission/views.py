# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.utils import translation
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods

from mangrove.errors.MangroveException import MangroveException, SubmissionParseException, FormModelDoesNotExistsException, NumberNotRegisteredException, DataObjectNotFound, SMSParserInvalidFormatException, MultipleSubmissionsForSameCodeException, UnknownOrganization, SMSParserWrongNumberOfAnswersException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.player.parser import SMSParserFactory
from mangrove.transport.player.player import SMSPlayer, TransportInfo

from datawinners.accountmanagement.models import OrganizationSetting, Organization, TEST_REPORTER_MOBILE_NUMBER, MessageTracker
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_database_manager, get_db_manager_for, get_organization_settings_for
from datawinners.messageprovider.messages import exception_messages, SMS
from datawinners.submission.models import DatawinnerLog, SMSResponse
from datawinners.messageprovider.message_handler import get_exception_message_for

import logging
logger = logging.getLogger("django")

@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def sms(request):
    message = Responder().respond(request)
    return HttpResponse(message)


class Responder(object):

    def __init__(self):
        self.next_state_processor = find_dbm

    def respond(self, incoming_request):
        request = self.next_state_processor(incoming_request)
        if request.get('outgoing_message'):
            return request['outgoing_message']

        self.next_state_processor = request['next_state']
        return self.respond(request)


def find_dbm(request):
    _from, _to = _get_from_and_to_numbers(request) #This is the http post request. After this state, the request being sent is a python dictionary
    incoming_request = {'incoming_message': request.POST["message"],
                        'datawinner_log': DatawinnerLog(message=request.POST["message"], from_number=_from,
                                                        to_number=_to)}

    if _to is None:
        incoming_request['outgoing_message'] = ugettext("Your organization does not have a telephone number assigned. Please contact DataWinners Support.")
        return incoming_request
    incoming_request['transport_info'] = TransportInfo(transport=SMS, source=_from, destination=_to)
    try:
        incoming_request['dbm'] = get_database_manager(request.user) if _from == TEST_REPORTER_MOBILE_NUMBER else get_db_manager_for(_from, _to)

    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        incoming_request['outgoing_message'] = incoming_request['datawinner_log'].error = message
        incoming_request['datawinner_log'].save()
        return incoming_request

    incoming_request['organization'] = _find_organization(request)
    incoming_request['next_state'] = increment_message_counter
    return incoming_request

def increment_message_counter(incoming_request):
    organization = incoming_request['organization']
    current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
    message_tracker = organization.get_message_tracker(current_month)
    message_tracker.increment_incoming_message_count()
    message_tracker.increment_outgoing_message_count()
    if not message_tracker.should_handle_message():
        incoming_request['outgoing_message'] = ugettext("You have used up your 100 SMS for the trial account. Please upgrade to a monthly subscription to continue sending in data to your projects.")
        return incoming_request

    incoming_request['next_state'] = find_parser
    return incoming_request

def find_parser(incoming_request):
    incoming_message = incoming_request['incoming_message']
    dbm = incoming_request['dbm']
    sms_parser = SMSParserFactory().getSMSParser(message=incoming_message,
                                                 dbm=dbm)
    try:
        form_code, values = sms_parser.parse(incoming_message)
        form_model = get_form_model_by_code(dbm, form_code)
        incoming_request['form_model'] = form_model
        incoming_request['submission_values'] = values
        incoming_request['datawinner_log'].form_code = form_code
    except SMSParserWrongNumberOfAnswersException as exception:
        form_model = get_form_model_by_code(dbm, exception.data[0])
        translation.activate(form_model.activeLanguages[0])
        message = get_exception_message_for(exception=exception, channel=SMS)
        incoming_request['outgoing_message'] = incoming_request['datawinner_log'].error = message
        incoming_request['datawinner_log'].save()
    except (SubmissionParseException,SMSParserInvalidFormatException,MultipleSubmissionsForSameCodeException) as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        incoming_request['outgoing_message'] = incoming_request['datawinner_log'].error = message
        incoming_request['datawinner_log'].save()
    except FormModelDoesNotExistsException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
        incoming_request['outgoing_message'] = incoming_request['datawinner_log'].error = message
        incoming_request['datawinner_log'].save()

    incoming_request['next_state'] = activate_language
    return incoming_request

def activate_language(incoming_request):
    translation.activate(incoming_request['form_model'].activeLanguages[0])
    incoming_request['next_state'] = submit_to_player
    return incoming_request

def submit_to_player(incoming_request):
    try:
        sms_player = SMSPlayer(incoming_request['dbm'], get_location_tree())
        response = sms_player.accept(incoming_request['transport_info'], incoming_request['form_model'].form_code, incoming_request['submission_values'])
        message = SMSResponse(response).text()
    except (SubmissionParseException, FormModelDoesNotExistsException,) as exception:
        message = incoming_request['datawinner_log'].error = get_exception_message_for(exception=exception, channel=SMS)
        incoming_request['datawinner_log'].save()
    except NumberNotRegisteredException as exception:
        message = incoming_request['datawinner_log'].error = get_exception_message_for(exception=exception, channel=SMS)
        incoming_request['datawinner_log'].save()
    except DataObjectNotFound as exception:
        message1 = ugettext(exception_messages.get(DataObjectNotFound).get(SMS))
        message = message1 % (incoming_request['form_model'].entity_type[0], exception.data[1], incoming_request['form_model'].entity_type[0])
    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel=SMS)
    except Exception as exception:
        logger.exception('SMS Processing failure: message')
        message = get_exception_message_for(exception=exception, channel=SMS)

    incoming_request['outgoing_message'] = message
    return incoming_request


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

def _find_organization(request):
    if request.POST.get('test_mode'):
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        return organization

    _from = request.POST["from_msisdn"]
    _to = request.POST["to_msisdn"]
    return get_organization_settings_for(_from, _to).organization