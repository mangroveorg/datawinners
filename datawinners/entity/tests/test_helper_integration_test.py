from django.contrib.auth.models import User
from django.utils import unittest
from mangrove.utils.types import is_empty
from mock import Mock
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from datawinners.entity.helper import delete_datasender_users_if_any

class TestEntityHelper(unittest.TestCase):

    def setUp(self):
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


    def tearDown(self):
        User.objects.filter(username=self.username).delete()

