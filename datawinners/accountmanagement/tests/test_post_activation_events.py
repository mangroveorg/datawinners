from django_countries.fields import Country
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from django.utils import unittest
from mangrove.form_model.form_model import REPORTER
from mock import Mock, patch
from datawinners.accountmanagement.models import DataSenderOnTrialAccount
from datawinners.accountmanagement.post_activation_events import make_user_as_a_datasender
from datawinners.accountmanagement.post_activation_events import active_organization
from datawinners.accountmanagement.models import NGOUserProfile, Organization
from django.contrib.auth.models import User

class TestPostActivationEvents(unittest.TestCase):
    def setUp(self):
        self.username = 'user_for_active@org.com'
        self.paid_user, _ = User.objects.get_or_create(username=self.username,email=self.username,password='1')
        self.paid_user.save()
        self.paid_org = Organization(name='test_org_for_correct_active_date', sector='PublicHealth', address='add', city='city', country=Country('MG'),
        zipcode='10000', active_date=None)
        self.paid_org.save()
        self.mobile_number = "1233"
        self.paid_user_profile = NGOUserProfile(user=self.paid_user, title='Mr.', org_id=self.paid_org.org_id,mobile_phone=self.mobile_number)
        self.paid_user_profile.save()

        self.trial_username = 'user_for_trial@org.com'
        self.trial_user, _ = User.objects.get_or_create(username=self.trial_username,email=self.trial_username,password='1')
        self.trial_user.save()

        self.trial_org = Organization(name='trial_org', sector='PublicHealth', address='add', city='city', country=Country('MG'),
        zipcode='10000', active_date=None, in_trial_mode=True,org_id='test')
        self.trial_org.save()

        self.trial_mobile_number = "12445"
        self.trial_user_profile = NGOUserProfile(user=self.trial_user, title='Mr.', org_id=self.trial_org.org_id,mobile_phone=self.trial_mobile_number)
        self.trial_user_profile.save()

        self.patcher1 = patch('datawinners.accountmanagement.post_activation_events.get_entity_count_for_type')
        self.get_all_entities_mock = self.patcher1.start()

        self.patcher2 = patch('datawinners.accountmanagement.post_activation_events.create_entity')
        self.create_entity_mock = self.patcher2.start()

        self.patcher3 = patch('datawinners.accountmanagement.post_activation_events.get_datadict_type_by_slug')
        self.get_datadict_type_by_slug = self.patcher3.start()

    def test_active_organization_with_should_active_date_is_none_save_active_date(self):
        active_organization(org = self.paid_org)
        self.assertIsNotNone(Organization.objects.get(org_id=self.paid_org.org_id).active_date)
        self.assertEqual(Organization.objects.get(org_id=self.paid_org.org_id).active_date.microsecond,0)

    def test_should_make_datasender_entity_for_paid_account(self):
        mock_manager = Mock(spec=DatabaseManager)
        entity_mock = Mock(spec=Entity)
        entity_mock.type_path = [REPORTER]
        self.get_all_entities_mock.return_value = 1
        self.create_entity_mock = entity_mock
        self.get_datadict_type_by_slug.return_value = Mock()

        make_user_as_a_datasender(mock_manager, self.paid_org, self.username,
            self.mobile_number)

        entity_mock.add_data.assert_called_once()

    def test_should_make_datasender_entity_and_datasender_on_trial_account_for_trial_account(self):
        mock_manager = Mock(spec=DatabaseManager)
        entity_mock = Mock(spec=Entity)
        entity_mock.type_path = [REPORTER]
        self.get_all_entities_mock.return_value = 1
        self.create_entity_mock = entity_mock
        self.get_datadict_type_by_slug.return_value = Mock()

        make_user_as_a_datasender(mock_manager, self.trial_org, self.trial_username,
            self.trial_mobile_number)

        entity_mock.add_data.assert_called_once()

        data_senders_on_trial_account = DataSenderOnTrialAccount.objects.filter(organization=self.trial_org)
        self.assertEqual(1,len(data_senders_on_trial_account))
        self.assertEqual(self.trial_mobile_number,data_senders_on_trial_account[0].mobile_number)
        self.assertEqual(self.trial_org,data_senders_on_trial_account[0].organization)


    def tearDown(self):
        self.paid_user_profile.delete()
        self.paid_org.delete()
        self.paid_user.delete()

        self.trial_user_profile.delete()
        self.trial_org.delete()
        self.trial_user.delete()
        DataSenderOnTrialAccount.objects.filter(organization=self.trial_org).delete()

        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
