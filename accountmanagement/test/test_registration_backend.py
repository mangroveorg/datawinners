import unittest
from django.conf import settings

from mock import Mock
from registration import signals
from datawinners.accountmanagement.registration_backend import RegistrationBackend
from registration.models import RegistrationProfile


class TestRegistrationBackend(unittest.TestCase):
    def setUp(self):
        self.backend = RegistrationBackend()
        self.request = Mock()


    SUBSCRIBED_ORGANIZATION_PARAMS = {'organization_name': 'myCompany',
                                          'organization_sector': 'Public Health',
                                          'organization_address': 'myAddress',
                                          'organization_city': 'xian',
                                          'organization_state': 'state',
                                          'organization_country': 'china',
                                          'organization_zipcode': '1234',
                                          'organization_office_phone': '1234567',
                                          'organization_website': 'abc.com',
                                          }

    TRIAL_ORGANIZATION_PARAMS = {'organization_name': 'myCompany',
                                 'organization_sector': 'Public Health',
                                 'organization_city': 'xian',
                                 'organization_country': 'china',
                                 }

    def test_creation_of_trial_organization(self):
        org = self.backend.create_respective_organization(self.TRIAL_ORGANIZATION_PARAMS)
        self.assertTrue(org.in_trial_mode, 'is not in trial mode')

    def test_creation_of_subscribed_organization(self):
        org = self.backend.create_respective_organization(self.SUBSCRIBED_ORGANIZATION_PARAMS)
        self.assertFalse(org.in_trial_mode, 'is in trial mode')

    def test_sms_number_for_new_subscribed_organisation_is_left_unset(self):
        organization = self.backend.create_respective_organization(self.SUBSCRIBED_ORGANIZATION_PARAMS)
        self.assertIsNone(organization.organization_setting.sms_tel_number)

    def test_email_for_new_subscribed_organization_does_not_contain_universal_phone_number(self):
        self._stub_code_for_email_content_test(trial_mode = False)

        user = self.backend.register(self.request, **self.SUBSCRIBED_ORGANIZATION_PARAMS)

        email_content = self._get_email_contents(user)
        self.assertNotRegexpMatches(email_content, 'You can also send your data via sms to')

    def test_email_for_new_trial_organisation_contains_universal_phone_number(self):
        self._stub_code_for_email_content_test(trial_mode = True)

        user = self.backend.register(self.request, **self.TRIAL_ORGANIZATION_PARAMS)

        email_content = self._get_email_contents(user)
        self.assertRegexpMatches(email_content, 'You can also send your data via sms to 1-775-237-4679')

    def _stub_code_for_email_content_test(self, **kwargs):
        user = Mock()
        organization = Mock()
        registration_profile = Mock()
        registration_profile.activation_key = 'ALREADY_ACTIVATED'
        RegistrationProfile.objects.get = Mock(return_value=registration_profile)
        user.activation_key = '_not_relevant_'
        self.backend._create_user = Mock(return_value=user)
        self.backend.create_respective_organization = Mock(return_value=organization)
        organization.in_trial_mode = kwargs.get('trial_mode') or False
        signals.user_registered.send = Mock()

    def _get_email_contents(self, user):
        self.assertTrue(user.email_user.called, 'method "email_user" was not called')
        args_from_call, kwargs_from_call = user.email_user.call_args
        email_content = args_from_call[1]
        return email_content

