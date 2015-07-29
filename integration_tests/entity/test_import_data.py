from django_countries.fields import Country
from mock import Mock
from nose.plugins.attrib import attr
from unittest import TestCase
from datawinners.accountmanagement.models import Organization, DataSenderOnTrialAccount
from datawinners.entity.import_data import FilePlayer
from framework.utils.common_utils import random_number
from framework.utils.database_manager_postgres import DatabaseManager
from mangrove.errors.MangroveException import MultipleReportersForANumberException


class TestImportDatasenderValidations(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trial_org = Organization(name='trial_org', sector='PublicHealth', address='add', city='city', country=Country('MG'),
        zipcode='10000', active_date=None, account_type='Basic',org_id='test')
        cls.trial_org.save()

    @classmethod
    def tearDownClass(cls):
        cls.trial_org.delete()

    @attr('integration_tests')
    def test_should_validate_duplicate_datasender(self):
        extension = '.xlsx'
        dbm = Mock(spec=DatabaseManager)
        player = FilePlayer.build(dbm, extension)
        mobile_number = random_number()
        data_sender = DataSenderOnTrialAccount.objects.model(mobile_number=mobile_number, organization=self.trial_org)
        data_sender.save(force_insert=True)
        with self.assertRaises(MultipleReportersForANumberException):
            player._import_data_sender(None, self.trial_org, {'m': mobile_number, 'l': []})