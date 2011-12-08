import unittest

from mock import Mock
from datawinners.accountmanagement.registration_backend import RegistrationBackend


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