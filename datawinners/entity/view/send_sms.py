import json
import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from datawinners import utils
from datawinners.accountmanagement.decorators import session_not_expired, is_not_expired
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.database import get_database_manager
from datawinners.project.helper import broadcast_message
from datawinners.scheduler.smsclient import NoSMSCException


class SendSMS(View):

    def _other_numbers(self, request):
        numbers = map(lambda i: i.strip(), request.POST['others'].split(","))
        return list(set(numbers))

    def post(self, request, *args, **kwargs):
        manager = get_database_manager(request.user)
        sms_text = request.POST['sms-text']
        other_numbers = self._other_numbers(request)
        organization = utils.get_organization(request)
        organization_setting = OrganizationSetting.objects.get(organization=organization)
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = organization._get_message_tracker(current_month)
        no_smsc = True
        failed_numbers = []
        try:
            failed_numbers = broadcast_message([], sms_text, organization_setting.get_organisation_sms_number()[0],
                               other_numbers, message_tracker, country_code=organization.get_phone_country_code())
        except NoSMSCException:
            no_smsc = True


        successful = len(failed_numbers) == 0 and not no_smsc

        return HttpResponse(json.dumps({'successful': successful, 'nosmsc': no_smsc, 'failednumbers': failed_numbers}))

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(SendSMS, self).dispatch(*args, **kwargs)
