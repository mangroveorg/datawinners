from unittest import TestCase

from celery.tests.case import MagicMock
from mock import Mock, patch, PropertyMock

from datawinners.accountmanagement.mobile_number_validater import MobileNumberValidater, validation_message_dict
from datawinners.accountmanagement.models import Organization
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.errors.MangroveException import NumberNotRegisteredException
from mangrove.transport.repository.reporters import REPORTER_ENTITY_TYPE


class TestMobileNumberValidater(TestCase):

    @classmethod
    def setUpClass(cls):
        organization = Mock(Organization)
        mobile_number = "12345678"
        reporter_id = "reporter_id"
        cls.mobile_number_validator = MobileNumberValidater(organization, mobile_number, reporter_id)

    def test_should_return_false_if_datasender_present_with_same_number(self):
        with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
            manager = MagicMock(spec=DatabaseManager)
            manager.load_all_rows_in_view.return_value = [{'key': ['12345678', 'name', 'rep_id'], 'value':None}]
            get_db_manager.return_value = manager
            self.assertFalse(self.mobile_number_validator.is_mobile_number_unique_for_the_account())

    def test_should_return_true_if_no_datasender_present_with_same_number(self):
        with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
            manager = MagicMock(spec=DatabaseManager)
            manager.load_all_rows_in_view.return_value = []
            get_db_manager.return_value = manager
            self.assertTrue(self.mobile_number_validator.is_mobile_number_unique_for_the_account())

    def test_should_return_true_if_datasender_with_same_number_is_only_the_user_being_edited(self):
        with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
            manager = MagicMock(spec=DatabaseManager)
            manager.load_all_rows_in_view.return_value = [{'key': ['12345678', 'name', 'reporter_id'], 'value':None}]
            get_db_manager.return_value = manager
            self.assertTrue(self.mobile_number_validator.is_mobile_number_unique_for_the_account())

    def test_should_validate_the_mobile_number_for_trial_account_if_unique(self):
        org = Mock(spec=Organization)
        type(org).in_trial_mode = PropertyMock(return_value=True)
        validator = MobileNumberValidater(org, "56789", "rep")
        with patch("datawinners.accountmanagement.mobile_number_validater.get_data_senders_on_trial_account_with_mobile_number") as get_data_senders_on_trial_account_with_mobile_number:
            with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
                manager = MagicMock(spec=DatabaseManager)
                manager.load_all_rows_in_view.return_value = []
                get_db_manager.return_value = manager
                get_data_senders_on_trial_account_with_mobile_number.return_value = []
                self.assertTrue(validator.validate())

    def test_should_validate_the_mobile_number_for_trial_account_if_not_unique(self):
        org = Mock(spec=Organization)
        type(org).in_trial_mode = PropertyMock(return_value=True)
        validator = MobileNumberValidater(org, "56789", "rep")
        with patch("datawinners.accountmanagement.mobile_number_validater.get_data_senders_on_trial_account_with_mobile_number") as get_data_senders_on_trial_account_with_mobile_number:
            with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
                manager = MagicMock(spec=DatabaseManager)
                manager.load_all_rows_in_view.return_value = []
                get_db_manager.return_value = manager
                get_data_senders_on_trial_account_with_mobile_number.return_value = [{'key': ['12345678', 'name', 'some_other_id'], 'value':None}]
                valid, message = validator.validate()
                self.assertFalse(valid)
                self.assertEquals(message, validation_message_dict['duplicate_in_different_account'])

    def test_should_validate_the_mobile_number_for_paid_account_if_unique(self):
        org = Mock(spec=Organization)
        type(org).in_trial_mode = PropertyMock(return_value=False)
        validator = MobileNumberValidater(org, "56789", "rep")
        manager = MagicMock(spec=DatabaseManager)
        with patch("datawinners.accountmanagement.mobile_number_validater.find_reporters_by_from_number") as find_reporters_by_from_number:
            with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
                datasender = Entity(manager,REPORTER_ENTITY_TYPE, short_code='reporter_id')
                find_reporters_by_from_number.return_value = [datasender]
                manager = MagicMock(spec=DatabaseManager)
                manager.load_all_rows_in_view.return_value = []
                get_db_manager.return_value = manager
                valid, message = validator.validate()
                self.assertFalse(valid)

    def test_should_validate_the_mobile_number_for_paid_account_if_not_unique(self):
        org = Mock(spec=Organization)
        type(org).in_trial_mode = PropertyMock(return_value=False)
        validator = MobileNumberValidater(org, "56789", "rep")
        with patch("datawinners.accountmanagement.mobile_number_validater.find_reporters_by_from_number") as find_reporters_by_from_number:
            with patch("datawinners.accountmanagement.mobile_number_validater.get_database_manager_for_org") as get_db_manager:
                find_reporters_by_from_number.return_value = []
                find_reporters_by_from_number.side_effect = NumberNotRegisteredException("12345678")
                manager = MagicMock(spec=DatabaseManager)
                manager.load_all_rows_in_view.return_value = []
                get_db_manager.return_value = manager
                self.assertTrue(validator.validate())

