from django.utils.translation import ugettext_lazy as _

from datawinners.accountmanagement.models import get_data_senders_on_trial_account_with_mobile_number
from datawinners.utils import get_database_manager_for_org
from mangrove.errors.MangroveException import NumberNotRegisteredException
from mangrove.transport.repository.reporters import find_reporters_by_from_number
from mangrove.utils.types import is_empty


validation_message_dict = {'duplicate_in_different_account': _('Sorry, this number has already been used for a different DataWinners Basic account.'),
                           'duplicate_in_same_account': _('Sorry, the telephone number %s has already been registered.'),
                           'paid_account_duplicate': _("This phone number is already in use. Please supply a different phone number")}
class MobileNumberValidater:
    def __init__(self, organization, mobile_number, reporter_id=None):
        self.reporter_id = reporter_id
        self.mobile_number = mobile_number
        self.organization = organization

    def is_mobile_number_unique_for_trial_account(self):
        if not is_empty(get_data_senders_on_trial_account_with_mobile_number(self.organization, self.mobile_number)):
            return False, validation_message_dict['duplicate_in_different_account']
        if not self.is_mobile_number_unique_for_the_account():
            return False, validation_message_dict['duplicate_in_same_account'] % self.mobile_number
        return True, ''

    def is_mobile_number_unique_for_the_account(self):
        dbm = get_database_manager_for_org(self.organization)
        datasenders = dbm.load_all_rows_in_view("datasender_by_mobile", start_key=[self.mobile_number], end_key=[self.mobile_number, {}, {}])
        if len(datasenders) == 0 or self.is_the_datasender_is_current_user(datasenders):
            return True
        return False

    def is_mobile_number_unique_for_paid_account(self):
        manager = get_database_manager_for_org(self.organization)
        try:
            registered_reporters = find_reporters_by_from_number(manager, self.mobile_number)
        except NumberNotRegisteredException:
            return True, ''
        if len(registered_reporters) == 1 and registered_reporters[0].short_code == self.reporter_id:
            return True, ''
        return False, validation_message_dict['paid_account_duplicate']

    def validate(self):
        if self.organization.in_trial_mode:
            return self.is_mobile_number_unique_for_trial_account()
        return self.is_mobile_number_unique_for_paid_account()

    def is_the_datasender_is_current_user(self, datasenders):
        return len(datasenders) == 1 and datasenders[0]['key'][1] == self.reporter_id