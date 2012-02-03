# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.accountmanagement.models import Organization, NGOUserProfile

def get_trial_account_user_phone_numbers():
    trial_orgs = Organization.objects.filter(in_trial_mode=True)
    phone_numbers = []
    for org in trial_orgs:
        profiles = NGOUserProfile.objects.filter(org_id=org.org_id)
        phone_numbers.extend([profile.mobile_phone for profile in profiles])
    return phone_numbers