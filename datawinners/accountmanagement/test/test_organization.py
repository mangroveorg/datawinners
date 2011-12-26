import unittest
import datetime
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator

class TestOrganization(unittest.TestCase):
    
    def setUp(self):
        self.organization = self._prepare_organization()

    def tearDown(self):
        self.organization.delete()

    def test_should_increment_message_count(self):
        self.organization.increment_all_message_count()
        message_tracker = self._get_current_message_tracker_of_organization()
        self.assertEquals(1,message_tracker.incoming_sms_count)
        self.assertEquals(1,message_tracker.outgoing_sms_count)

        message_tracker = self._get_current_message_tracker_of_organization()
        message_tracker.incoming_sms_count = 3
        message_tracker.outgoing_sms_count = 3
        message_tracker.save()

        self.organization.increment_all_message_count()
        message_tracker = self._get_current_message_tracker_of_organization()
        self.assertEquals(4,message_tracker.incoming_sms_count)
        self.assertEquals(4,message_tracker.outgoing_sms_count)

    def test_should_check_trial_org_message_count(self):
        self.assertFalse(self.organization.has_exceed_message_limit())
        message_tracker = self._get_current_message_tracker_of_organization()
        message_tracker.incoming_sms_count = 51
        message_tracker.outgoing_sms_count = 51
        message_tracker.save()
        self.assertTrue(self.organization.has_exceed_message_limit())

    def _prepare_organization(self):
        trial_organization = Organization(name='test_org_for_trial_account',
                                                            sector='PublicHealth', address='add',
                                                            city='Pune', country='India',
                                                            zipcode='411006', in_trial_mode=True,
                                                            org_id=OrganizationIdCreator().generateId())
        trial_organization.save()
        return trial_organization

    def _get_current_message_tracker_of_organization(self):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self.organization._get_message_tracker(current_month)
        return message_tracker

