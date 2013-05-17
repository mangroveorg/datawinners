from django.core.exceptions import ObjectDoesNotExist
from datawinners.accountmanagement.models import OrganizationSetting, DataSenderOnTrialAccount
from datawinners.countrytotrialnumbermapping.helper import get_trial_numbers
import re

class OrganizationFinder(object):
    def find(self, from_number, to_number):
        to_number = re.sub("(\-)|(\+)", "", to_number)
        from_number = re.sub("(\-)|(\+)", "", from_number)
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


    def find_organization_setting(self, number):
        organization_settings = self._find_organization_settings(number)
        for os in organization_settings:
            if number in [re.sub("(\-)|(\+)", "", num.strip()) for num in os.sms_tel_number.split(',')]:
                return os
        return None

    def find_paid_organization(self, to_number):
        organization_setting = self.find_organization_setting(to_number)
        return (organization_setting.organization, None) if organization_setting is not None else (None, u'No organization found for telephone number %s' % (to_number,))

    def _find_organization_settings(self, number):
        return OrganizationSetting.objects.filter(sms_tel_number__contains=number)

    def find_organization_setting_includes_trial_account(self, to_tel):
        orgs = filter(lambda x: to_tel in x.get_organisation_sms_number(), OrganizationSetting.objects.all());
        return orgs[0] if len(orgs) else None