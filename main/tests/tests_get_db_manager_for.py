import unittest
from datawinners.accountmanagement.models import DataSenderOnTrialAccount
from datawinners.main.utils import get_db_manager_for
from django.conf import settings

class TestGetDBManagerFor(unittest.TestCase):
    def setUp(self):
        pass

    # returns database manager based on organization phone number for paid accounts
    def test_get_dbm_based_on_org_number_for_paid_accounts(self):
        org_tel_number = "919880734937"
        dbm = get_db_manager_for(None, org_tel_number)
        self.assertIsNotNone(dbm)

    def test_get_dbm_based_on_datasender_number_for_trial_accounts(self):
        data_sender_phone_no = "1234567890"
        DataSenderOnTrialAccount(mobile_number=data_sender_phone_no, organization_id="COJ00000").save()
        org_tel_number = settings.TRIAL_ACCOUNT_PHONE_NUMBER
        dbm = get_db_manager_for(data_sender_phone_no, org_tel_number)
        self.assertIsNotNone(dbm)
