import os
os.environ['DJANGO_SETTINGS_MODULE'] = "datawinners.settings"
print os.environ

from django.contrib.auth.models import User
import sys
from accountmanagement.models import OrganizationSetting, Organization, NGOUserProfile

email = "rhmino@gmail.com"
users = User.objects.filter(email=email)
if not users:
    print '%s is not a registered user in datawinners.' % email
    sys.exit(0)

ngo_user_profile = NGOUserProfile.objects.filter(user=users[0])[0]
organization = Organization.objects.filter(org_id=ngo_user_profile.org_id)
organization_setting = OrganizationSetting.objects.filter(organization=organization)

print 'Document store found: %s\n' % organization_setting.document_store

