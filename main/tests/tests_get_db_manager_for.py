import unittest
from datawinners.accountmanagement.models import DataSenderOnTrialAccount, OrganizationSetting, Organization
from datawinners.main.utils import get_db_manager_for
from django.conf import settings
from mangrove.datastore.database import get_db_manager

class TestGetDBManagerFor(unittest.TestCase):
    def setUp(self):
        pass

    # returns database manager based on organization phone number for paid accounts
    def test_get_dbm_based_on_org_number_for_paid_accounts(self):
        org_tel_number = "919880734937"
        dbm = get_db_manager_for(None, org_tel_number)
        expectedbm = get_db_manager(server=settings.COUCH_DB_SERVER, database='hni_testorg_slx364903')
        self.assertEqual(dbm, expectedbm)

    def test_get_dbm_based_on_data_sender_number_for_trial_accounts(self):

        data_sender_phone_no = "1234567890"
        data_sender = DataSenderOnTrialAccount(mobile_number=data_sender_phone_no, organization_id="COJ00000")
        data_sender.save()
        org_tel_number = settings.TRIAL_ACCOUNT_PHONE_NUMBER
        dbm = get_db_manager_for(data_sender_phone_no, org_tel_number)
        expectdbm = get_db_manager(server=settings.COUCH_DB_SERVER, database='hni_testorg_coj00000')
        data_sender.delete()
        self.assertEqual(dbm, expectdbm)