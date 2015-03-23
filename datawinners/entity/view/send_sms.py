import json
import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.database import get_database_manager
from datawinners.project.helper import broadcast_message
from datawinners.scheduler.smsclient import NoSMSCException


class SendSMS(View):
    def _other_numbers(self, request):
        if request.POST['recipient'] == 'others':
            numbers = map(lambda i: i.strip(), request.POST['others'].split(","))
            return list(set(numbers))

        return []

    def mobile_numbers_for_questionnaire(self, dbm, questionnaire_names):
        es = Elasticsearch()
        search = Search(using=es, index=dbm.database_name, doc_type='reporter')
        search = search.fields('mobile_number')
        search = search.query("terms", projects_value=questionnaire_names)
        search = search.query("term", void=False)
        body = search.to_dict()
        response = es.search(index=dbm.database_name, doc_type='reporter', body=body)

        return [item['fields']['mobile_number'] for item in response['hits']['hits']]

    def _get_mobile_numbers_for_registered_data_senders(self, dbm, request):
        if request.POST['recipient'] == 'linked':
            questionnaire_names = map(lambda item: item.lower(), json.loads(request.POST['questionnaire-names']))
            mobile_numbers = self.mobile_numbers_for_questionnaire(dbm, questionnaire_names)
            return mobile_numbers
        else:
            return []

    def post(self, request, *args, **kwargs):
        dbm = get_database_manager(request.user)
        sms_text = request.POST['sms-text']
        other_numbers = self._other_numbers(request)
        organization = utils.get_organization(request)
        organization_setting = OrganizationSetting.objects.get(organization=organization)
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = organization._get_message_tracker(current_month)
        no_smsc = False
        mobile_numbers = self._get_mobile_numbers_for_registered_data_senders(dbm, request)

        failed_numbers = []
        try:
            failed_numbers = broadcast_message(mobile_numbers, sms_text,
                                               organization_setting.get_organisation_sms_number()[0],
                                               other_numbers, message_tracker,
                                               country_code=organization.get_phone_country_code())
        except NoSMSCException:
            no_smsc = True

        successful = len(failed_numbers) == 0 and not no_smsc

        return HttpResponse(json.dumps({'successful': successful, 'nosmsc': no_smsc, 'failednumbers': failed_numbers}))

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(SendSMS, self).dispatch(*args, **kwargs)


def _get_all_contacts_mobile_numbers(dbm):
    es = Elasticsearch()
    search = Search(using=es, index=dbm.database_name, doc_type='reporter')
    search = search.fields('mobile_number')
    search = search.query("term", void=False)
    body = search.to_dict()
    response = es.search(index=dbm.database_name, doc_type='reporter', body=body)

    return [item['fields']['mobile_number'] for item in response['hits']['hits']]


def get_all_mobile_numbers(request):
    dbm = get_database_manager(request.user)
    mobile_numbers = _get_all_contacts_mobile_numbers(dbm)
    return HttpResponse(json.dumps({'mobile_numbers': ", ".join(mobile_numbers)}))
