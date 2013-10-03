from django.contrib.auth.models import User
from mock import Mock

from mangrove.contrib.registration import create_default_reg_form_model
from mangrove.datastore.entity import Entity
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from mangrove.utils.types import is_empty
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.entity.helper import delete_datasender_users_if_any, put_email_information_to_entity


class TestEntityHelper(MangroveTestCase):

    def setUp(self):
        MangroveTestCase.setUp(self)
        self.username = 'a@a.com'
        self.datasender_user, _ = User.objects.get_or_create(username=self.username,email=self.username,password='1')
        self.datasender_user.save()

        self.mobile_number = '112233'
        self.org_id = "test_org"
        self.reporter_id = "rptr1"
        self.datasender_user_profile = NGOUserProfile(user=self.datasender_user, title='Mr.',
                                org_id=self.org_id, mobile_phone=self.mobile_number, reporter_id = self.reporter_id)
        self.datasender_user_profile.save()

    def test_should_delete_the_datasender_user_if_it_exists(self):
        self.assertTrue(User.objects.get(username=self.username))
        self.assertTrue(NGOUserProfile.objects.get(reporter_id=self.reporter_id, org_id=self.org_id))
        entity_ids = [self.reporter_id, 'test_id']
        organization = Mock(spec=Organization)
        organization.org_id = self.org_id
        delete_datasender_users_if_any(entity_ids, organization)
        self.assertTrue(is_empty(User.objects.filter(username=self.username)))
        self.assertTrue(is_empty(NGOUserProfile.objects.filter(reporter_id=self.reporter_id, org_id=self.org_id)))

    def test_should_add_email_to_datasender(self):
        email = "tester@test.com"
        entity = Entity(self.manager, entity_type=REPORTER_ENTITY_TYPE, short_code="short_code")
        entity.save()
        create_default_reg_form_model(self.manager)

        put_email_information_to_entity(self.manager, entity, email=email)

        entity_values = entity.data
        self.assertEquals(entity_values["email"]["value"], email)

    def tearDown(self):
        MangroveTestCase.tearDown(self)
        User.objects.filter(username=self.username).delete()

