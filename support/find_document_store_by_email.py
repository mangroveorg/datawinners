import os
os.environ['DJANGO_SETTINGS_MODULE'] = "datawinners.settings"

from django.contrib.auth.models import User
import sys
from datawinners.accountmanagement.models import OrganizationSetting, Organization, NGOUserProfile

email = "rhmino@gmail.com"
users = User.objects.filter(email=email)
if not users:
    print '%s is not a registered user in datawinners.' % email
    sys.exit(0)

ngo_user_profile = NGOUserProfile.objects.filter(user=users[0])[0]
organization = Organization.objects.filter(org_id=ngo_user_profile.org_id)[0]
organization_setting = OrganizationSetting.objects.filter(organization=organization)[0]

print 'Document store found: %s' % organization_setting.document_store
print 'Organization name is: %s' % organization.name

