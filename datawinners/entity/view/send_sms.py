import ast
import json
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired, is_datasender
from datawinners.accountmanagement.models import OrganizationSetting, NGOUserProfile
from datawinners.main.database import get_database_manager
from datawinners.project.helper import broadcast_message
from datawinners.scheduler.smsclient import NoSMSCException
from datawinners.search.all_datasender_search import get_all_datasenders_search_results
from datawinners.sent_message.models import PollInfo
from datawinners.utils import strip_accents, lowercase_and_strip_accents
from mangrove.datastore.entity import contact_by_short_code


class SendSMS(View):
    def _other_numbers(self, request):
        if request.POST['recipient'] == 'others':
            numbers = map(lambda i: i.strip(), request.POST['others'].split(","))
            return list(set(numbers))

        return []

    def _mobile_numbers_for_questionnaire(self, dbm, questionnaire_names):
        search_parameters = {'void': False, 'search_filters': {'projects': questionnaire_names}}
        return _get_all_contacts_mobile_numbers(dbm, search_parameters)

    def get_contact_details(self, dbm, request):
        questionnaire_names = map(lambda item: lowercase_and_strip_accents(item),
                                      json.loads(request.POST['questionnaire-names']))
        search_parameters = {'void': False, 'search_filters': {'projects': questionnaire_names}}
        mobile_numbers, contact_display_list = _get_all_contacts_details(dbm, search_parameters)
        return mobile_numbers, contact_display_list

    def _mobile_numbers_for_groups(self, dbm, group_names):
        search_parameters = {'void': False, 'search_filters': {'group_names': group_names}}
        return _get_all_contacts_mobile_numbers(dbm, search_parameters)

    def _get_mobile_number_for_contacts(self, dbm, poll_recipients):
        poll_recipients = ast.literal_eval(poll_recipients)
        mobile_numbers = []
        for poll_recipient in poll_recipients:
            contact = contact_by_short_code(dbm, poll_recipient)
            mobile_numbers.append(contact.data.get('mobile_number')['value'])
        return mobile_numbers




    def _get_mobile_numbers_for_registered_data_senders(self, dbm, request):
        if request.POST['recipient'] == 'linked':
            questionnaire_names = map(lambda item: lowercase_and_strip_accents(item),
                                      json.loads(request.POST['questionnaire-names']))
            mobile_numbers = self._mobile_numbers_for_questionnaire(dbm, questionnaire_names)
            return mobile_numbers
        else:
            return []

    def _get_mobile_numbers_for_specific_contacts(self, dbm, request):
        if request.POST['recipient'] == 'specific-contacts':
            numbers = map(lambda i: i.strip(), request.POST['others'].split(","))
            return numbers
        else:
            return []


    def _get_mobile_numbers_for_groups(self, dbm, request):
        if request.POST['recipient'] == 'group':
            group_names = json.loads(request.POST['group-names'])
            mobile_numbers = self._mobile_numbers_for_groups(dbm, group_names)
            return mobile_numbers
        else:
            return []


    def _get_sender_details(self, organization_setting):
        return NGOUserProfile.objects.filter(org_id=organization_setting.organization.org_id)[
                   0].user.first_name + " ("+ \
               NGOUserProfile.objects.filter(org_id=organization_setting.organization.org_id)[0].reporter_id + ")"

    def _log_poll_questionnaire_sent_messages(self, dbm, organization, organization_setting, request, sms_text, current_project_id, failed_numbers):
        mobile_numbers, contact_dict = get_contact_details(dbm, request, failed_numbers)
        user_profile = self._get_sender_details(organization_setting)
        if mobile_numbers:
            self._save_sent_message_info(organization.org_id, datetime.datetime.now(), sms_text, contact_dict,
                                     user_profile, current_project_id)

    def post(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        sms_text = request.POST['sms-text']
        other_numbers = self._other_numbers(request)
        organization = utils.get_organization(request)
        organization_setting = OrganizationSetting.objects.get(organization=organization)
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = organization._get_message_tracker(current_month)
        no_smsc = False
        mobile_numbers_for_ds_linked_to_questionnaire = self._get_mobile_numbers_for_registered_data_senders(dbm,
                                                                                                             request)
        mobile_numbers_for_specific_contacts = self._get_mobile_numbers_for_specific_contacts(dbm, request)
        mobile_numbers_for_ds_linked_to_group = self._get_mobile_numbers_for_groups(dbm, request)
        mobile_numbers_for_ds = self._get_mobile_number_for_contacts(dbm, request.POST['my_poll_recipients'])
        mobile_numbers = mobile_numbers_for_ds_linked_to_questionnaire + mobile_numbers_for_ds_linked_to_group + mobile_numbers_for_specific_contacts + mobile_numbers_for_ds

        failed_numbers = []
        try:
            failed_numbers = broadcast_message(mobile_numbers, sms_text,
                                               organization_setting.get_organisation_sms_number()[0],
                                               other_numbers, message_tracker,
                                               country_code=organization.get_phone_country_code())
            # log sent messages only for poll questionnaire
            current_project_id = json.loads(request.POST['project_id'])
            if current_project_id != "":
                self._log_poll_questionnaire_sent_messages(dbm, organization, organization_setting, request, sms_text, current_project_id, failed_numbers)

        except NoSMSCException:
            no_smsc = True

        successful = len(failed_numbers) == 0 and not no_smsc

        return HttpResponse(json.dumps({'successful': successful, 'nosmsc': no_smsc, 'failednumbers': failed_numbers}))

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(SendSMS, self).dispatch(*args, **kwargs)

    def _save_sent_message_info(self, org_id, sent_on, sms_text, to_mobile_numbers, from_mobile_numbers, questionnaire_name):
        poll_info_message = PollInfo(org_id=org_id, sent_on=sent_on, message=sms_text,
                                             recipients=str(to_mobile_numbers), sender=str(from_mobile_numbers),  questionnaire_id=questionnaire_name)
        poll_info_message.save()

def _get_all_contacts_mobile_numbers(dbm, search_parameters):
    search_parameters['response_fields'] = ['mobile_number']
    search_results = get_all_datasenders_search_results(dbm, search_parameters)
    return [item['mobile_number'] for item in search_results.hits]

def get_name_short_code_mobile_numbers_for_contacts(dbm, poll_recipients):
    poll_recipients = ast.literal_eval(poll_recipients)
    mobile_numbers = []
    contact_dict_list = []
    for poll_recipient in poll_recipients:
        contact = contact_by_short_code(dbm, poll_recipient)
        mobile_numbers.append(contact.data.get('mobile_number')['value'])
        if contact.name != "":
             contact_dict_list.append("%s (%s)" % (contact.name, contact.short_code))
        else:
            contact_dict_list.append("%s (%s)" % (contact.data['mobile_number']['value'], contact.short_code))
    return mobile_numbers, contact_dict_list

def get_contact_details(dbm, request, failed_numbers):
        mobile_numbers = []
        contact_display_list = []
        search_parameters = {}
        if request.POST['recipient'] == 'linked':
            questionnaire_names = map(lambda item: lowercase_and_strip_accents(item),
                                      json.loads(request.POST['questionnaire-names']))
            search_parameters = {'void': False, 'search_filters': {'projects': questionnaire_names}}
            mobile_numbers, contact_display_list = _get_all_contacts_details_with_mobile_number(dbm, search_parameters, failed_numbers)
        elif request.POST['recipient'] == 'group':
            group_names = json.loads(request.POST['group-names'])
            search_parameters = {'void': False, 'search_filters': {'group_name': group_names}}
            mobile_numbers, contact_display_list = _get_all_contacts_details_with_mobile_number(dbm, search_parameters, failed_numbers)

        elif request.POST['recipient'] == 'poll_recipients':
            mobile_numbers, contact_display_list = get_name_short_code_mobile_numbers_for_contacts(dbm, request.POST['my_poll_recipients'])

        return mobile_numbers, contact_display_list


def _get_all_contacts_details(dbm, search_parameters):
    search_parameters['response_fields'] = ['short_code', 'name', 'mobile_number']
    search_results = get_all_datasenders_search_results(dbm, search_parameters)
    mobile_numbers, contact_display_list = [], []

    for entry in search_results.hits:
        mobile_numbers.append(entry['mobile_number'])
        display_prefix = entry['name'] if entry.get('name') else entry['mobile_number']
        contact_display_list.append("%s (%s)" % (display_prefix, entry['short_code']))

    return mobile_numbers, contact_display_list

def _get_all_contacts_details_with_mobile_number(dbm, search_parameters, failed_numbers):
    search_parameters['response_fields'] = ['short_code', 'name', 'mobile_number']
    search_results = get_all_datasenders_search_results(dbm, search_parameters)
    mobile_numbers, contact_display_list = [], []

    for entry in search_results.hits:
        if entry['mobile_number'] not in failed_numbers:
            mobile_numbers.append(entry['mobile_number'])
            display_prefix = entry['name'] if entry.get('name') else entry['mobile_number']
            contact_display_list.append("%s (%s)" % (display_prefix, entry['short_code']))

    return mobile_numbers, contact_display_list


@login_required
@session_not_expired
@is_datasender
@is_not_expired
def get_all_mobile_numbers(request):
    dbm = get_database_manager(request.user)
    search_parameters = {'group_name': request.POST.get('group_name'), 'query_string': request.POST.get('search_query')}
    mobile_numbers, contact_display_list = _get_all_contacts_details(dbm, search_parameters)
    response = {'mobile_numbers': ", ".join(mobile_numbers), 'contact_display_list': ", ".join(contact_display_list)}
    return HttpResponse(json.dumps(response))
