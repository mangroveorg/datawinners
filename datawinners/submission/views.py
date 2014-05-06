# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
import iso8601
from mangrove.transport.contract.request import Request
from mangrove.errors.MangroveException import DataObjectAlreadyExists, DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.transport.player.player import SMSPlayer
from django.utils import translation
from mangrove.transport.repository.reporters import find_reporter_entity
from mangrove.errors.MangroveException import ExceedSMSLimitException, ExceedSubmissionLimitException

from datawinners.accountmanagement.decorators import is_not_expired
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.smsapi.accounting import is_chargable
from datawinners.submission.models import  SMSResponse
from datawinners.utils import get_organization
from datawinners.messageprovider.handlers import create_failure_log
from datawinners.submission.organization_finder import OrganizationFinder
from datawinners.submission.request_processor import    MangroveWebSMSRequestProcessor, SMSMessageRequestProcessor, SMSTransportInfoRequestProcessor, get_vumi_parameters
from datawinners.submission.submission_utils import PostSMSProcessorLanguageActivator, PostSMSProcessorNumberOfAnswersValidators
from datawinners.submission.submission_utils import PostSMSProcessorCheckDSIsLinkedToProject
from datawinners.submission.submission_utils import PostSMSProcessorCheckDSIsRegistered, PostSMSProcessorCheckLimits
from datawinners.utils import  get_database_manager_for_org
from datawinners.location.LocationTree import get_location_hierarchy, get_location_tree
from datawinners.feeds.database import get_feeds_db_for_org
from datawinners.feeds.mail_client import mail_feed_errors
from datawinners.messageprovider.exception_handler import handle
from datawinners.submission.location import LocationBridge
from datawinners.settings import NEAR_SUBMISSION_LIMIT_TRIGGER, NEAR_SMS_LIMIT_TRIGGER, LIMIT_TRIAL_ORG_SUBMISSION_COUNT
from datawinners.project.utils import is_quota_reached
from datawinners.sms.models import SMS, MSG_TYPE_SUBMISSION_REPLY, MSG_TYPE_USER_MSG, MSG_TYPE_REMINDER, MSG_TYPE_API
from mangrove.errors.MangroveException import SMSParserWrongNumberOfAnswersException

logger = logging.getLogger("django")

couter_map={
    MSG_TYPE_USER_MSG:'send_message_charged_count',
    MSG_TYPE_REMINDER:'sent_reminders_charged_count',
    MSG_TYPE_SUBMISSION_REPLY:'outgoing_sms_charged_count',
    MSG_TYPE_API:'sms_api_usage_charged_count'
}

@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def receipt(request):
    if request.POST.get("callback_name") == u"sms_receipt":
        message = ""
        try:
            sms = SMS.objects.get(message_id=request.POST.get("id"))
            sms.status = request.POST.get('transport_status')
            if not sms.smsc: sms.smsc = request.POST.get('transport_name')
            sms.delivered_at = iso8601.parse_date(request.POST.get('delivered_at'))
            sms.save()
            if is_chargable(sms.status, sms.smsc):
                counter = couter_map.get(sms.msg_type, '')
                if counter:
                    sms.organization.increment_message_count_for(**{counter:1})
        except Exception as e:
            message = e.message
        return HttpResponse(message)
    return HttpResponse("NA")

@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
def sms(request):
    message = Responder().respond(request)
    if not message:
        return HttpResponse(status=403)
    response = HttpResponse(message)
    response['X-Vumi-HTTPRelay-Reply'] = 'true'
    response['Content-Length'] = len(response.content)
    return response


@login_required
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
    incoming_request['message_id'] = request.POST.get('message_id')
    translation.activate(organization.language)

    incoming_request['next_state'] = check_account_and_datasender
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
    incoming_request['test_sms_questionnaire'] = True

    if is_quota_reached(request, organization=incoming_request.get('organization')):
        incoming_request['outgoing_message'] = ''
        return incoming_request

    incoming_request['next_state'] = check_account_and_datasender
    import logging

    websubmission_logger = logging.getLogger("websubmission")
    incoming_request["logger"] = websubmission_logger
    return incoming_request


def check_account_and_datasender(incoming_request):
    organization = incoming_request['organization']

    if organization.status == 'Deactivated' or organization.is_expired():
        incoming_request['outgoing_message'] = ''
        return incoming_request

    try:
        reporter_entity = find_reporter_entity(incoming_request.get('dbm'), incoming_request.get('transport_info').source)
        incoming_request['reporter_entity'] = reporter_entity
        check_quotas_for_trial(incoming_request)
    except Exception as e:
        incoming_request['exception'] = e

    if not incoming_request.get('test_sms_questionnaire'):
        organization.increment_all_message_count()
        
    incoming_request['next_state'] = submit_to_player
    return incoming_request

def check_quotas_for_trial(incoming_request):
    organization = incoming_request.get('organization')
    if organization.has_exceeded_submission_limit():
        raise ExceedSubmissionLimitException()

    if organization.has_exceeded_message_limit():
        raise ExceedSMSLimitException()

def check_quotas_and_update_users(organization, sms_channel=False):
    if organization.in_trial_mode and organization.get_total_submission_count() == NEAR_SUBMISSION_LIMIT_TRIGGER:
        organization.send_mail_to_organization_creator(email_type='about_to_reach_submission_limit')

    if organization.in_trial_mode and sms_channel and \
        organization.get_total_incoming_message_count() == NEAR_SMS_LIMIT_TRIGGER:
        organization.send_mail_to_organization_creator(email_type='about_to_reach_sms_limit')

    if organization.in_trial_mode and organization.get_total_submission_count() == LIMIT_TRIAL_ORG_SUBMISSION_COUNT:
        organization.send_mail_to_organization_creator(email_type='reached_submission_limit')

def log_sms_and_increment_counters(incoming_request, log):
    if log: create_failure_log(incoming_request.get('outgoing_message'), incoming_request)
    organization = incoming_request.get('organization')
    organization.increment_message_count_for(outgoing_sms_count=1, incoming_sms_count=1, sms_registration_count=1)

def send_message(incoming_request, response):
    ReportRouter().route(incoming_request['organization'].org_id, response)


def submit_to_player(incoming_request):
    sent_via_sms_test_questionnaire = incoming_request.get('test_sms_questionnaire', False)
    organization = incoming_request.get('organization')
    organization = organization

    try:
        dbm = incoming_request['dbm']
        post_sms_parser_processors = [PostSMSProcessorLanguageActivator(dbm, incoming_request),
                                      PostSMSProcessorCheckDSIsRegistered(dbm, incoming_request)]
        if organization.in_trial_mode:
            post_sms_parser_processors.append(PostSMSProcessorCheckLimits(dbm, incoming_request))

        post_sms_parser_processors.extend([PostSMSProcessorCheckDSIsLinkedToProject(dbm, incoming_request),
                                            PostSMSProcessorNumberOfAnswersValidators(dbm, incoming_request)])
        
        sms_player = SMSPlayer(dbm, LocationBridge(get_location_tree(), get_loc_hierarchy=get_location_hierarchy),
            post_sms_parser_processors=post_sms_parser_processors, feeds_dbm=incoming_request['feeds_dbm'])
        mangrove_request = Request(message=incoming_request['incoming_message'],
            transportInfo=incoming_request['transport_info'])
        response = sms_player.accept(mangrove_request, logger=incoming_request.get("logger"))

        if response.is_registration and not sent_via_sms_test_questionnaire:
            organization.increment_message_count_for(sms_registration_count=1)

        if not response.is_registration:
            if sent_via_sms_test_questionnaire:
                organization.increment_message_count_for(incoming_web_count=1)
            check_quotas_and_update_users(organization, sms_channel=True)

        mail_feed_errors(response, dbm.database_name)
        message = SMSResponse(response).text(dbm)
        send_message(incoming_request, response)
    except DataObjectAlreadyExists as e:
        message = ugettext("Error. %s already exists. Register your %s with a different Identification Number.") % \
                  (e.data[1], e.data[2].capitalize())
        if not sent_via_sms_test_questionnaire:
            organization.increment_message_count_for(sms_registration_count=1)

    except DataObjectNotFound as exception:
        if sent_via_sms_test_questionnaire:
            organization.increment_message_count_for(incoming_web_count=1)
        message = handle(exception, incoming_request)

    except FormModelDoesNotExistsException as exception:
        if sent_via_sms_test_questionnaire:
            organization.increment_message_count_for(incoming_web_count=1)
        message = handle(exception, incoming_request)

    except SMSParserWrongNumberOfAnswersException as exception:
        form_model = sms_player.get_form_model(mangrove_request)
        if not form_model.is_entity_registration_form():
            organization.increment_message_count_for(incoming_web_count=1) if sent_via_sms_test_questionnaire else organization.increment_message_count_for(incoming_sms_count=1)
        elif not sent_via_sms_test_questionnaire:
                organization.increment_message_count_for(sms_registration_count=1)
        message = handle(exception, incoming_request)

    except Exception as exception:
        if sent_via_sms_test_questionnaire:
            organization.increment_message_count_for(incoming_web_count=1)
        message = handle(exception, incoming_request)

    message = incoming_request.get('error_message', message)
    incoming_request['outgoing_message'] = message

    if not sent_via_sms_test_questionnaire:
        SMS(message= message,
            message_id=incoming_request['message_id'],
            organization=incoming_request['organization'],
            msg_from = mangrove_request.transport.source,
            msg_to= mangrove_request.transport.destination,
            msg_type=MSG_TYPE_SUBMISSION_REPLY,
            status="Submitted").save()

    return incoming_request


def _get_organization(request):
    _from, _to = _get_from_and_to_numbers(request)
    return OrganizationFinder().find(_from, _to)


def _get_from_and_to_numbers(request):
    vumi_parameters = get_vumi_parameters(request)
    return vumi_parameters.from_number, vumi_parameters.to_number
