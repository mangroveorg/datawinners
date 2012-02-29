import unittest
from datawinners.submission.organization_finder import OrganizationFinder
from datawinners.tests.data import TRIAL_ACCOUNT_ORGANIZATION_ID, TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, DEFAULT_TEST_ORG_TEL_NO, DEFAULT_TEST_ORG_ID
from countrytotrialnumbermapping.helper import get_trial_numbers
from countrytotrialnumbermapping.models import Network

class TestOrganizationFinder(unittest.TestCase):
    def setUp(self):
        self.trial_numbers = get_trial_numbers()
        
    def test_should_find_organization_for_trial_account(self):
        organization,error = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, self.trial_numbers[0])
        # this organization is created in test data
        self.assertEqual(TRIAL_ACCOUNT_ORGANIZATION_ID,organization.org_id)

    def test_should_return_error_when_datasender_is_not_registered_for_trial_account(self):
        organization,error = OrganizationFinder().find("123", self.trial_numbers[1])
        # this organization is created in test data
        self.assertEqual(u"Sorry, this number 123 is not registered with us.",error)

    def test_should_return_the_same_trial_organization_if_sms_sent_to_any_trial_account_number(self):
        trial_organization1,error1 = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, self.trial_numbers[0])
        trial_organization2,error2 = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, self.trial_numbers[1])
        self.assertEqual(trial_organization1, trial_organization2)

    def test_should_return_error_when_organization_doesnot_exists(self):
        organization,error = OrganizationFinder().find("123", "678")
        # this organization is created in test data
        self.assertEqual(u'No organization found for telephone number 678',error)

    def test_should_return_organization(self):
        organization,error = OrganizationFinder().find("123", DEFAULT_TEST_ORG_TEL_NO)
        # this organization is created in test data
        self.assertEqual(DEFAULT_TEST_ORG_ID,organization.org_id)

    def test_should_find_organization_with_new_trial_number(self):
        new_number = "12345678"
        new_network = Network(trial_sms_number=new_number, network_name="airtel")
        new_network.save()
        organization,error = OrganizationFinder().find(TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, new_number)
        self.assertEqual(organization.org_id, TRIAL_ACCOUNT_ORGANIZATION_ID)
