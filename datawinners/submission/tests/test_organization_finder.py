import unittest
from django.conf import settings
from django.test import TestCase
from datawinners.submission.organization_finder import OrganizationFinder
from datawinners.tests.data import TRIAL_ACCOUNT_ORGANIZATION_ID, TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, DEFAULT_TEST_ORG_TEL_NO, DEFAULT_TEST_ORG_ID


class TestOrganizationFinder(TestCase):

    fixtures = ['test_data.json']

    def setUp(self):
        self.trial_number = settings.TRIAL_ACCOUNT_PHONE_NUMBER[0]
        
    def test_should_find_organization_for_trial_account(self):
        organization,error = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, self.trial_number)
        # this organization is created in test data
        self.assertEqual(TRIAL_ACCOUNT_ORGANIZATION_ID,organization.org_id)

    def test_should_return_error_when_datasender_is_not_registered_for_trial_account(self):
        organization,error = OrganizationFinder().find("123", self.trial_number)
        # this organization is created in test data
        expected = u"Error. You are not registered as a Data Sender. Please contact your supervisor."
        self.assertEqual(expected, error)

    def test_should_return_the_same_trial_organization_if_sms_sent_to_any_trial_account_number(self):
        trial_organization1,error1 = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, self.trial_number)
        trial_organization2,error2 = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, self.trial_number)
        self.assertEqual(trial_organization1, trial_organization2)

    def test_should_return_error_when_organization_doesnot_exists(self):
        organization,error = OrganizationFinder().find("123", "678")
        # this organization is created in test data
        self.assertEqual(u'No organization found for telephone number 678',error)

    def test_should_return_organization(self):
        organization,error = OrganizationFinder().find("123", DEFAULT_TEST_ORG_TEL_NO)
        # this organization is created in test data
        self.assertEqual(DEFAULT_TEST_ORG_ID,organization.org_id)
