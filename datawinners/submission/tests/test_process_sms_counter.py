import unittest
import datetime
from datawinners.accountmanagement.models import Organization
from datawinners.submission.views import process_sms_counter
from datawinners.tests.data import TRIAL_ACCOUNT_ORGANIZATION_ID

class TestProcessSMSCounter(unittest.TestCase):
    def setUp(self):
        self.incoming_request ={}
        self.incoming_request['outgoing_message']=''
        self.incoming_request['organization']= Organization.objects.get(pk=TRIAL_ACCOUNT_ORGANIZATION_ID)

    def test_should_go_to_next_state_when_message_limit_does_not_exceeds(self):
        self.incoming_request = process_sms_counter(self.incoming_request)
        self.assertEquals(self.incoming_request['outgoing_message'],'')

    def test_should_return_outgoing_message_when_message_limit_exceeds(self):
        message_tracker = self._get_current_message_tracker_of_organization()
        message_tracker.incoming_sms_count = 50
        message_tracker.outgoing_sms_count = 50
        message_tracker.save()
        self.incoming_request = process_sms_counter(self.incoming_request)
        self.assertEquals(self.incoming_request['outgoing_message'],"You have used up your 100 SMS for the trial account. Please upgrade to a monthly subscription to continue sending in data to your projects.")

    def _get_current_message_tracker_of_organization(self):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self.incoming_request['organization']._get_message_tracker(current_month)
        return message_tracker

    def test_should_return_outgoing_message_when_organization_is_deactivated(self):
        self.incoming_request['organization'].status = 'Deactivated'
        self.assertEqual(self.incoming_request['organization'].status, 'Deactivated')
        self.incoming_request = process_sms_counter(self.incoming_request)
        self.assertEquals(self.incoming_request['outgoing_message'], '')

