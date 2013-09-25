from datetime import datetime
import unittest
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.template.defaultfilters import slugify
from django_digest.models import PartialDigest
from mock import Mock, PropertyMock
from accountmanagement.admin import DWUserAdmin
from accountmanagement.models import Organization, OrganizationSetting, NGOUserProfile
from accountmanagement.organization_id_creator import OrganizationIdCreator

class FakeUserAdmin(DWUserAdmin):
    class Meta:
        proxy = True

    def __init__(self, org_id):
        self.org_id = org_id


class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.user = self._prepare_test_user()
        self.org_id=OrganizationIdCreator().generateId()
        self.create_organization()
        self.admin = FakeUserAdmin(self.org_id)


    def tearDown(self):
        User.objects.get(username='a@a.com').delete()

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
                                    in_trial_mode = True,
                                    active_date = datetime(2011,07,11))
        organization.save()
        self.organization_setting = OrganizationSetting()
        self.organization_setting.organization = organization
        self.organization_setting.document_store = slugify("%s_%s_%s" % ("HNI", organization.name, self.org_id))
        self.organization_setting.save()

    def test_should_delete_partial_digests_if_email_edited(self):
        request = Mock(spec=WSGIRequest)
        obj = User.objects.get(username='a@a.com')
        obj.email = 'b@a.com'
        form = Mock()
        changed_data = PropertyMock(return_value=['email'])
        type(form).changed_data = changed_data
        cleaned_data = PropertyMock(return_value={'organization_id':self.org_id})
        type(form).cleaned_data = cleaned_data
        self.admin.save_model(request, obj, form, True)
        self.assertRaises(PartialDigest.DoesNotExist,PartialDigest.objects.get,user=self.user)


    def test_should_not_delete_partial_digests_if_anything_other_than_email_edited(self):
        request = Mock(spec=WSGIRequest)
        obj = User.objects.get(username='a@a.com')
        obj.first_name = 'b'
        form = Mock()
        changed_data = PropertyMock(return_value=['first_name'])
        type(form).changed_data = changed_data
        cleaned_data = PropertyMock(return_value={'organization_id':self.org_id})
        type(form).cleaned_data = cleaned_data
        self.admin.save_model(request, obj, form, True)
        self.assertEquals(PartialDigest.objects.get(user=self.user), self.digest)

    def _prepare_test_user(self):
        user = User(username='a@a.com', first_name='a', last_name='a', email='a@a.com', password='password')
        user.save()
        (NGOUserProfile(user=user)).save()
        digest = PartialDigest(user=user, login='a@a.com', partial_digest='partial', confirmed=True)
        digest.save()
        self.digest = digest
        return user