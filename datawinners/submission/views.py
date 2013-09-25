# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from datawinners.accountmanagement.decorators import is_not_expired

from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.submission.models import  SMSResponse
from datawinners.utils import get_organization
from datawinners.messageprovider.handlers import create_failure_log
from datawinners.submission.organization_finder import OrganizationFinder
from datawinners.submission.request_processor import    MangroveWebSMSRequestProcessor, SMSMessageRequestProcessor, SMSTransportInfoRequestProcessor, get_vumi_parameters
from datawinners.submission.submission_utils import PostSMSProcessorLanguageActivator, PostSMSProcessorNumberOfAnswersValidators
from datawinners.utils import  get_database_manager_for_org
from datawinners.location.LocationTree import get_location_hierarchy, get_location_tree
from datawinners.feeds.database import get_feeds_db_for_org
from datawinners.feeds.mail_client import mail_feed_errors
from mangrove.transport.contract.request import Request
from datawinners.messageprovider.exception_handler import handle
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.transport.player.player import SMSPlayer
from datawinners.submission.location import LocationBridge
from mangrove.transport.repository.reporters import find_reporter_entity
from django.utils import translation
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.player.parser import SMSParserFactory


logger = logging.getLogger("django")

@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def sms(request):
    message = Responder().respond(request)
    response = HttpResponse(message)
    response['X-Vumi-HTTPRelay-Reply'] = 'true' if message else 'false'
    response['Content-Length'] = len(response.content)
    return response


@login_required(login_url='/login')
@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@is_not_expired
def web_sms(request):
    message = Responder(next_state_processor=find_dbm_for_web_sms).respond(request)
    return HttpResponse(message)


def find_dbm(request):
    incoming_request = {}
    #This is the http post request. After this state, the request being sent is a python dictionary
    SMSMessageRequestProcessor().process(http_request=request, mangrove_request=incoming_request)
    SMSTransportInfoRequestProcessor().process(http_request=request, mangrove_request=incoming_request)
    organization, error = _get_organization(request)

    if error is not None:
        incoming_request['outgoing_message'] = error
        create_failure_log(error, incoming_request)
        return incoming_request

    incoming_request['dbm'] = get_database_manager_for_org(organization)
    incoming_request['feeds_dbm'] = get_feeds_db_for_org(organization)
    incoming_request['organization'] = organization

    incoming_request['next_state'] = process_sms_counter
    return incoming_request


class Responder(object):
    def __init__(self, next_state_processor=find_dbm):
        self.next_state_processor = next_state_processor

    def respond(self, incoming_request):
        request = self.next_state_processor(incoming_request)
        if request.has_key('outgoing_message'):
            return request['outgoing_message']

        self.next_state_processor = request['next_state']
        return self.respond(request)


def find_dbm_for_web_sms(request):
    incoming_request = dict()
    MangroveWebSMSRequestProcessor().process(http_request=request, mangrove_request=incoming_request)
    incoming_request['organization'] = get_organization(request)
    incoming_request['next_state'] = submit_to_player
    import logging

    websubmission_logger = logging.getLogger("websubmission")
    incoming_request["logger"] = websubmission_logger
    return incoming_request


def process_sms_counter(incoming_request):
    organization = incoming_request['organization']

    if organization.status == 'Deactivated':
        organization.increment_message_count_for(**{'incoming_sms_count':1})
        incoming_request['outgoing_message'] = ''
        return incoming_request

    organization.increment_all_message_count()

    if organization.has_exceeded_message_limit():
        return get_translated_response_message(incoming_request,
            "You have reached your 50 SMS Submission limit. Please upgrade to a monthly subscription to continue sending in SMS Submissions to your projects.")

    incoming_request['next_state'] = submit_to_player
    return incoming_request


def get_translated_response_message(incoming_request, original_message):
    message = incoming_request.get('incoming_message')
    dbm = incoming_request.get('dbm')
    parser = SMSParserFactory().getSMSParser(message, dbm)
    parsing_result = parser.parse(message)
    form_model = get_form_model_by_code(dbm, parsing_result[0])
    translation.activate(form_model.activeLanguages[0])
    incoming_request['outgoing_message'] = ugettext(original_message)
    return incoming_request

def send_message(incoming_request, response):
    ReportRouter().route(incoming_request['organization'].org_id, response)


def submit_to_player(incoming_request):
    try:
        dbm = incoming_request['dbm']
        post_sms_parser_processors = [PostSMSProcessorLanguageActivator(dbm, incoming_request),
                                      PostSMSProcessorNumberOfAnswersValidators(dbm, incoming_request)]
        sms_player = SMSPlayer(dbm, LocationBridge(get_location_tree(), get_loc_hierarchy=get_location_hierarchy),
            post_sms_parser_processors=post_sms_parser_processors, feeds_dbm=incoming_request['feeds_dbm'])
        mangrove_request = Request(message=incoming_request['incoming_message'],
            transportInfo=incoming_request['transport_info'])
        response = sms_player.accept(mangrove_request, logger=incoming_request.get("logger"))
        mail_feed_errors(response, dbm.database_name)
        message = SMSResponse(response).text(dbm)
        send_message(incoming_request, response)
    except DataObjectAlreadyExists as e:
        message = ugettext("The Unique ID Number %s is already used for the %s %s. Register your %s with a different ID.") % \
                  (e.data[1], e.data[2], e.data[3], e.data[2])
    except Exception as exception:
        message = handle(exception, incoming_request)

    incoming_request['outgoing_message'] = message
    return incoming_request


def _get_organization(request):
    _from, _to = _get_from_and_to_numbers(request)
    return OrganizationFinder().find(_from, _to)


def _get_from_and_to_numbers(request):
    vumi_parameters = get_vumi_parameters(request)
    return vumi_parameters.from_number, vumi_parameters.to_number

