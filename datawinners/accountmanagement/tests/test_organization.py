import unittest
import datetime
from datawinners.accountmanagement.models import Organization
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator


class TestOrganization(unittest.TestCase):
    def setUp(self):
        self.organization = self._prepare_organization()

    def tearDown(self):
        self.organization.delete()

    def test_should_increment_sms_api_usage_count(self):
        self.organization.increment_sms_api_usage_count()
        message_tracker = self._get_current_message_tracker_of_organization()
        self.assertEquals(1, message_tracker.sms_api_usage_count)

    def test_should_increment_message_count(self):
        self.organization.increment_all_message_count()
        message_tracker = self._get_current_message_tracker_of_organization()
        self.assertEquals(1, message_tracker.incoming_sms_count)
        self.assertEquals(1, message_tracker.outgoing_sms_count)

        message_tracker = self._get_current_message_tracker_of_organization()
        message_tracker.incoming_sms_count = 3
        message_tracker.outgoing_sms_count = 3
        message_tracker.save()

        self.organization.increment_all_message_count()
        message_tracker = self._get_current_message_tracker_of_organization()
        self.assertEquals(4, message_tracker.incoming_sms_count)
        self.assertEquals(4, message_tracker.outgoing_sms_count)

    def test_should_check_trial_org_message_count(self):
        self.assertFalse(self.organization.has_exceeded_message_limit())
        message_tracker = self._get_current_message_tracker_of_organization()
        message_tracker.incoming_sms_count = 51
        message_tracker.outgoing_sms_count = 51
        message_tracker.save()
        self.assertTrue(self.organization.has_exceeded_message_limit())

    def _prepare_organization(self):
        trial_organization = Organization(name='test_org_for_trial_account',
                                          sector='PublicHealth', address='add',
                                          city='Pune', country='IN',
                                          zipcode='411006', in_trial_mode=True,
                                          org_id=OrganizationIdCreator().generateId())
        trial_organization.save()
        return trial_organization

    def _get_current_message_tracker_of_organization(self):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self.organization._get_message_tracker(current_month)
        return message_tracker

    def test_should_return_country_phone_code(self):
        country_code = self.organization.get_phone_country_code()
        self.assertEqual(country_code, "91")

    def test_should_increment_by_submission_type(self):
        increment_count_by_submission_type_dict = {'incoming_sms_count': 4,'incoming_sp_count':2, 'incoming_web_count':7}
        self.organization.increment_message_count_for(**increment_count_by_submission_type_dict)
        message_tracker = self._get_current_message_tracker_of_organization()
        for field_name, count in increment_count_by_submission_type_dict.items():
            self.assertEqual(getattr(message_tracker, field_name), count)
        
