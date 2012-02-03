# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from accountmanagement.models import Organization, NGOUserProfile

def get_trial_account_user_phone_numbers():
    trial_orgs = Organization.objects.filter(in_trial_mode=True)
    return [NGOUserProfile.objects.get(org_id=org.org_id).mobile_phone for org in trial_orgs]
