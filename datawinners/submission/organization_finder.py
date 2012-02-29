from django.core.exceptions import ObjectDoesNotExist
from datawinners.accountmanagement.models import OrganizationSetting, DataSenderOnTrialAccount
from countrytotrialnumbermapping.helper import get_trial_numbers

class OrganizationFinder(object):
    def find(self, from_number, to_number):
        if to_number in get_trial_numbers():
            return self.find_trial_account_organization(from_number)
        return self.find_paid_organization(to_number)

    def find_trial_account_organization(self, from_number):
        try:
            record = DataSenderOnTrialAccount.objects.get(mobile_number=from_number)
            organization_settings = OrganizationSetting.objects.get(organization=record.organization)
        except ObjectDoesNotExist:
            return None, (u"Sorry, this number %s is not registered with us.") % (from_number,)
        return organization_settings.organization, None


    def find_paid_organization(self, to_number):
        try:
            organization_settings = OrganizationSetting.objects.get(sms_tel_number=to_number)
        except ObjectDoesNotExist:
            return None, u'No organization found for telephone number %s' % (to_number,)
        return organization_settings.organization, None


