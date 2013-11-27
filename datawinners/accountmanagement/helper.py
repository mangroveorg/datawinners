# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.errors.MangroveException import NumberNotRegisteredException
from mangrove.utils.types import is_empty
from mangrove.transport.repository.reporters import find_reporters_by_from_number
from datawinners.accountmanagement.models import Organization, NGOUserProfile,\
    get_data_senders_on_trial_account_with_mobile_number, DataSenderOnTrialAccount
from datawinners.utils import get_database_manager_for_org

def get_trial_account_user_phone_numbers():
    trial_orgs = Organization.objects.filter(in_trial_mode=True)
    phone_numbers = []
    for org in trial_orgs:
        profiles = NGOUserProfile.objects.filter(org_id=org.org_id)
        phone_numbers.extend([profile.mobile_phone for profile in profiles])
    return phone_numbers

def get_unique_mobile_number_validator(organization):
    if organization.in_trial_mode:
        return is_mobile_number_unique_for_trial_account
    return is_mobile_number_unique_for_paid_account

def is_mobile_number_unique_for_trial_account(org,mobile_number):
    return is_empty(get_data_senders_on_trial_account_with_mobile_number(mobile_number)) and\
           mobile_number not in get_trial_account_user_phone_numbers()

def is_mobile_number_unique_for_paid_account(org,mobile_number):
    manager = get_database_manager_for_org(org)
    try:
        find_reporters_by_from_number(manager, mobile_number)
        return False
    except NumberNotRegisteredException:
        return True

def get_all_registered_phone_numbers_on_trial_account():
    return DataSenderOnTrialAccount.objects.values_list('mobile_number', flat=True)


def is_org_user(user):
    return user.groups.filter(name__in=["NGO Admins", "Project Managers"]).count() > 0
