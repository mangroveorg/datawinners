# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from mangrove.errors.MangroveException import NumberNotRegisteredException
from mangrove.datastore.database import DatabaseManager
from mock import Mock, patch
from datawinners.accountmanagement.helper import get_trial_account_user_phone_numbers, is_mobile_number_unique_for_paid_account, get_unique_mobile_number_validator, is_mobile_number_unique_for_trial_account
from datawinners.accountmanagement.models import Organization
from datawinners.tests.data import TRIAL_ACCOUNT_USERS_MOBILE_NUMBERS, TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO, DEFAULT_TEST_ORG_TEL_NO

class TestHelper(unittest.TestCase):

    def setUp(self):
        self.get_database_manager_for_org_patch = patch('datawinners.accountmanagement.helper.get_database_manager_for_org')
        self.get_database_manager_for_org_mock = self.get_database_manager_for_org_patch.start()
        self.find_reporters_by_from_number_patch = patch('datawinners.accountmanagement.helper.find_reporters_by_from_number')
        self.find_reporters_by_from_number_mock = self.find_reporters_by_from_number_patch.start()

    def tearDown(self):
        self.get_database_manager_for_org_patch.stop()
        self.find_reporters_by_from_number_patch.stop()


    def test_get_mobile_numbers_for_trial_account(self):
        self.assertSetEqual(set(TRIAL_ACCOUNT_USERS_MOBILE_NUMBERS),set(get_trial_account_user_phone_numbers()))

    def test_should_return_proper_mobile_number_unique_validator(self):
        org = Mock(spec=Organization)
        org.in_trial_mode = False
        self.assertEqual(is_mobile_number_unique_for_paid_account, get_unique_mobile_number_validator(org))
        org.in_trial_mode = True
        self.assertEqual(is_mobile_number_unique_for_trial_account, get_unique_mobile_number_validator(org))

    def test_should_validate_the_mobile_number_for_trial_account_if_not_unique(self):
        org = Mock(spec=Organization)
        org.account_type = 'Basic'
        validator = get_unique_mobile_number_validator(org)
        self.assertFalse(validator(org,TRIAL_ACCOUNT_DATA_SENDER_MOBILE_NO))

    def test_should_validate_the_mobile_number_for_trial_account_if_unique(self):
        org = Mock(spec=Organization)
        org.account_type = 'Basic'
        validator = get_unique_mobile_number_validator(org)
        self.assertTrue(validator(org,DEFAULT_TEST_ORG_TEL_NO))

    def test_should_validate_the_mobile_number_for_paid_account_if_not_unique(self):
        org = Mock(spec=Organization)
        org.in_trial_mode = False
        self.get_database_manager_for_org_mock.return_value = Mock(spec=DatabaseManager)
        validator = get_unique_mobile_number_validator(org)
        self.assertFalse(validator(org,'1234'))

    def test_should_validate_the_mobile_number_for_paid_account_if_unique(self):
        org = Mock(spec=Organization)
        org.account_type = 'Pro SMS'
        self.get_database_manager_for_org_mock.return_value = Mock(spec=DatabaseManager)
        self.find_reporters_by_from_number_mock.side_effect = NumberNotRegisteredException('1234')
        validator = get_unique_mobile_number_validator(org)
        self.assertTrue(validator(org,'1234'))
