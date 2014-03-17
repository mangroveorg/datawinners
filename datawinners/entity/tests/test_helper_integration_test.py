import unittest
from django.contrib.auth.models import User
from mangrove.bootstrap import initializer
from mangrove.datastore.database import get_db_manager
from mangrove.utils.test_utils.database_utils import delete_and_create_form_model, uniq
from mock import Mock

from mangrove.contrib.registration import create_default_reg_form_model, GLOBAL_REGISTRATION_FORM_CODE
from mangrove.datastore.entity import Entity
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE
from mangrove.utils.types import is_empty
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.entity.helper import delete_datasender_users_if_any, put_email_information_to_entity


class TestEntityHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manager = get_db_manager('http://localhost:5984/',uniq('mangrove-test'))
        initializer._create_views(cls.manager)
        cls.username = 'a@a.com'
        cls.datasender_user, _ = User.objects.get_or_create(username=cls.username,email=cls.username,password='1')
        cls.datasender_user.save()

        cls.mobile_number = '112233'
        cls.org_id = "test_org"
        cls.reporter_id = "rptr1"
        cls.datasender_user_profile = NGOUserProfile(user=cls.datasender_user, title='Mr.',
                                org_id=cls.org_id, mobile_phone=cls.mobile_number, reporter_id = cls.reporter_id)
        cls.datasender_user_profile.save()

    def test_should_add_email_to_datasender(self):
        email = "tester@test.com"
        entity = Entity(self.manager, entity_type=REPORTER_ENTITY_TYPE, short_code="short_code")
        entity.save()
        delete_and_create_form_model(self.manager, GLOBAL_REGISTRATION_FORM_CODE)

        put_email_information_to_entity(self.manager, entity, email=email)

        entity_values = entity.data
        self.assertEquals(entity_values["email"]["value"], email)

    def test_should_delete_the_datasender_user_if_it_exists(self):
        self.assertTrue(User.objects.get(username=self.username))
        self.assertTrue(NGOUserProfile.objects.get(reporter_id=self.reporter_id, org_id=self.org_id))
        entity_ids = [self.reporter_id, 'test_id']
        organization = Mock(spec=Organization)
        organization.org_id = self.org_id
        delete_datasender_users_if_any(entity_ids, organization)
        self.assertTrue(is_empty(User.objects.filter(username=self.username)))
        self.assertTrue(is_empty(NGOUserProfile.objects.filter(reporter_id=self.reporter_id, org_id=self.org_id)))


    @classmethod
    def tearDownClass(cls):
        User.objects.filter(username=cls.username).delete()

