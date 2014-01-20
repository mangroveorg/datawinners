import unittest
from mock import patch, Mock
from datawinners.accountmanagement.models import Organization, MessageTracker
from django.contrib.auth.models import User

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.message_tracker = MessageTracker()
        request = Mock()
        request.user = User.objects.get(pk=-12)
        self.request = request

    def test_should_return_false_if_quota_not_reached(self):
        message_tracker = self.message_tracker
        message_tracker.incoming_sms_count = 50
        message_tracker.incoming_sp_count = 30
        message_tracker.incoming_web_count = 25
        message_tracker.sms_registration_count = 4
        
        with patch.object(Organization, "_get_all_message_trackers") as patch_message_tracker:
            patch_message_tracker.return_value = [message_tracker]
            from datawinners.project.utils import is_quota_reached
            self.assertFalse(is_quota_reached(self.request))
            