from datetime import datetime
from django.template.defaultfilters import slugify
from nose.tools import raises
from datawinners.accountmanagement.forms import LoginForm
from datawinners.accountmanagement.models import Organization, NGOUserProfile, OrganizationSetting
from django.contrib.auth.models import User
from mangrove.errors.MangroveException import AccountExpiredException
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator

import unittest

class FakeUser(User):
    class Meta:
        proxy = True
    
    def __init__(self, org_id):
        self.org_id = org_id

    def get_profile(self):
        profile = NGOUserProfile()
        profile.org_id = self.org_id
        return profile

class FakeForm(LoginForm):
    def __init__(self, org_id):
        self.user_cache = FakeUser(org_id)

class TestLogin(unittest.TestCase):
    def create_organization(self):
        organization = Organization('organization_name',
                                    'organization_sector',
                                    'organization_address',
                                    'organization_city',
                                    'organization_state',
                                    'organization_country',
                                    'organization_zipcode',
                                    'organization_office_phone',
                                    'organization_website',
                                    org_id = self.org_id,
                                    account_type = 'Basic',
                                    active_date = datetime(2011,07,11))
        organization.save()
        self.organization_setting = OrganizationSetting()
        self.organization_setting.organization = organization
        self.organization_setting.document_store = slugify("%s_%s_%s" % ("HNI", organization.name, self.org_id))
        self.organization_setting.save()

    @raises(AccountExpiredException)
    def test_should_raise_a_trial_account_expired_exception_if_trial_account_is_expired(self):
        self.org_id=OrganizationIdCreator().generateId()
        self.create_organization()
        form = FakeForm(org_id = self.org_id)
        form.check_trial_account_expired()

    def tearDown(self):
        org = Organization.objects.get(org_id = self.org_id)
        self.organization_setting.delete()
        org.delete()
