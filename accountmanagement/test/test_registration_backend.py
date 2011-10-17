import unittest
from datawinners.accountmanagement.registration_backend import RegistrationBackend

__author__ = 'Thoughtworks'

class TestRegistrationBackend(unittest.TestCase):
    def test_creation_of_trial_organization(self):
        registration_backend = RegistrationBackend()
        org_details = {'organization_name': 'myCompany',
                       'organization_sector': 'Public Health',
                       'organization_city': 'xian',
                       'organization_country':'china',
                       }
        org = registration_backend.create_respective_organization(org_details)
        self.assertTrue(org.in_trial_mode, 'is not in trial mode')

    def test_creation_of_subscribed_organization(self):
        registration_backend = RegistrationBackend()
        org_details = {'organization_name': 'myCompany',
                       'organization_sector': 'Public Health',
                       'organization_address':'myAddress',
                       'organization_city': 'xian',
                       'organization_state':'state',
                       'organization_country':'china',
                       'organization_zipcode':'1234',
                       'organization_office_phone':'1234567',
                       'organization_website':'abc.com',
                       }
        org = registration_backend.create_respective_organization(org_details)
        self.assertFalse(org.in_trial_mode, 'is in trial mode')



  