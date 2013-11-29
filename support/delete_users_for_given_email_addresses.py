from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.entity.helper import delete_datasender_for_trial_mode
from datawinners.utils import get_database_manager_for_org
from mangrove.utils.types import is_not_empty

org_id = 'FFN411573'
email_addresses = ['ndarvech@unicef.org', 'srabotovao@unicef.org', 'handrianaivosoa@unicef.org', 'jratsimbazafy@unicef.org', 'eravelonjanahary@unicef.org',
                   'bonardbonard@unicef.org', 'lrazafindrakoto@unicef.org', 'jrabenantenaina@unicef.org', 'hrasolomanana@unicef.org',
                   'jrandriatefison@unicef.org', 'dralaivao@unicef.org', 'fsahoa@unicef.org', 'frakotomahanina@unicef.org', 'srakotondrina@unicef.org', 'srandrianarisoa@unicef.org',
                   'arazanakoto@unicef.org', 'lrasoamahenina@unicef.org', 'drasolofoniaina@unicef.org', 'nandry@unicef.org', 'mrajonson@unicef.org']

organization = Organization.objects.get(org_id=org_id)

print "Organization in trail mode:%s" % organization.in_trial_mode
dbm = get_database_manager_for_org(organization)


def _delete_user_entry(profiles):
    user_profile = profiles[0]
    profile_reporter_id = user_profile.reporter_id
    if profile_reporter_id.lower() == profile_reporter_id:
        print "Not deleting user since the reporter id is already lowercase."
    else:
        print "Deleting user."
        user_profile.user.delete()
        if organization.in_trial_mode:
            delete_datasender_for_trial_mode(dbm, [profile_reporter_id.lower()], 'reporter')

def _is_only_datasender(user):
    return user.groups.filter(name__in=["NGO Admins", "Project Managers"]).count() <= 0

for email_id in email_addresses:
    try:
        print "Processing User with email_id: '%s'" % email_id
        user = User.objects.get(email=email_id)
        if _is_only_datasender(user):
            profiles = NGOUserProfile.objects.filter(user=user)
            if is_not_empty(profiles):
                _delete_user_entry(profiles)
            else:
                print "User with email_id: '%s' has no profile" % user.email
        else:
            print "User with email_id: '%s' is not a simple DS and will not be deleted." % user.email
    except ObjectDoesNotExist:
         print "User with email_id: '%s' does not exist" % user.email