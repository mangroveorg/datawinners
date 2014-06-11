from django.test import TestCase, Client
from django.contrib.auth.models import User
from datawinners.accountmanagement.forms import UserProfileForm
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator


class TestUserRegistration(TestCase):
    def test_user_email_validation_should_be_case_insensitive(self):
        User.objects.create_user('User@user.com', 'User@user.com', 'password')
        trial_organization = Organization(name='test_org_for_trial_account',
                                  sector='PublicHealth', address='add',
                                  city='Pune', country='IN',
                                  zipcode='411006', account_type='Basic',
                                  org_id=OrganizationIdCreator().generateId(),
                                  status='Activated')
        trial_organization.save()

        form = UserProfileForm(organization=trial_organization,
                               data={'title': 'manager', 'full_name': 'user one', 'username': 'uSER@User.com',
                                     'mobile_phone': '7889522'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'],['This email address is already in use. Please supply a different email address'])

        form = UserProfileForm(organization=trial_organization,
                       data={'title': 'manager', 'full_name': 'user one', 'username': 'uSER1@User.com',
                             'mobile_phone': '7889522'})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_username(),'user1@user.com')