import unittest
import datetime
from datawinners.accountmanagement.models import Organization
from datawinners.submission.views import process_sms_counter
from datawinners.tests.data import TRIAL_ACCOUNT_ORGANIZATION_ID
from mock import patch
from datawinners.submission.views import check_quotas_and_update_users
from datawinners.settings import NEAR_SUBMISSION_LIMIT_TRIGGER, NEAR_SMS_LIMIT_TRIGGER
from django.core import mail
from django.contrib.auth.models import Group
from django.template.loader import render_to_string

class TestProcessSMSCounter(unittest.TestCase):
    def setUp(self):
        self.incoming_request ={}
        self.incoming_request['outgoing_message']=''
        self.incoming_request['incoming_message']=''
        self.incoming_request['organization']= Organization.objects.get(pk=TRIAL_ACCOUNT_ORGANIZATION_ID)
        self.outgoing_message = "You have reached your 50 SMS Submission limit. Please upgrade to a monthly subscription to continue sending in SMS Submissions to your projects."
        users = self.incoming_request['organization'].get_related_users()
        self.user = users[0]
        self.group = Group.objects.get(name='NGO Admins')
        self.group.user_set.add(self.user)

    def tearDown(self):
        self.group.user_set.remove(self.user)

    def test_should_go_to_next_state_when_message_limit_does_not_exceeds(self):
        self.incoming_request = process_sms_counter(self.incoming_request)
        self.assertEquals(self.incoming_request['outgoing_message'], '')

    def test_should_return_outgoing_message_when_message_limit_exceeds(self):
        message_tracker = self._get_current_message_tracker_of_organization()
        message_tracker.incoming_sms_count = 50
        message_tracker.outgoing_sms_count = 50
        message_tracker.save()
        with patch('datawinners.submission.views.get_translated_response_message') as mock_get_translated_response_message:
            self.incoming_request.update({'outgoing_message': self.outgoing_message})
            mock_get_translated_response_message.return_value = self.incoming_request
            self.incoming_request = process_sms_counter(self.incoming_request)
            self.assertEquals(self.incoming_request['outgoing_message'], self.outgoing_message)

    def _get_current_message_tracker_of_organization(self):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self.incoming_request['organization']._get_message_tracker(current_month)
        return message_tracker

    def test_should_return_outgoing_message_when_organization_is_deactivated(self):
        self.incoming_request['organization'].status = 'Deactivated'
        self.assertEqual(self.incoming_request['organization'].status, 'Deactivated')
        self.incoming_request = process_sms_counter(self.incoming_request)
        self.assertEquals(self.incoming_request['outgoing_message'], '')

    def test_should_send_mail_when_ngo_about_to_reach_submission_limit(self):
        organization = self.incoming_request.get('organization')
        with patch.object(Organization, "get_total_submission_count") as patch_get_total_submission_count:
            patch_get_total_submission_count.return_value = NEAR_SUBMISSION_LIMIT_TRIGGER
            check_quotas_and_update_users(organization=organization)
            email = mail.outbox.pop()
            self.assertEqual(['chinatwu2@gmail.com'], email.to)
            ctx = {'username':'Trial User', 'organization':organization, 'current_site':'localhost:8000'}
            self.assertEqual(render_to_string('email/basicaccount/about_to_reach_submission_limit_en.html', ctx), email.body)

    def test_should_send_mail_to_when_sms_limit_is_about_to_reached(self):
        organization = self.incoming_request.get('organization')
        with patch.object(Organization, "get_total_message_count") as patch_get_total_message_count:
            patch_get_total_message_count.return_value = NEAR_SMS_LIMIT_TRIGGER
            check_quotas_and_update_users(organization=organization, sms_channel=True)
            email = mail.outbox.pop()
            self.assertEqual(['chinatwu2@gmail.com'], email.to)
            ctx = {'username':'Trial User', 'organization':organization, 'current_site':'localhost:8000'}
            self.assertEqual(render_to_string('email/basicaccount/about_to_reach_sms_limit_en.html', ctx), email.body)

    def test_should_send_all_email_type_when_all_limit_are_about_to_reached(self):
        organization = self.incoming_request.get('organization')
        with patch.object(Organization, "get_total_submission_count") as patch_get_total_submission_count:
            with patch.object(Organization, "get_total_message_count") as patch_get_total_message_count:
                patch_get_total_submission_count.return_value = NEAR_SUBMISSION_LIMIT_TRIGGER
                patch_get_total_message_count.return_value = NEAR_SMS_LIMIT_TRIGGER
                check_quotas_and_update_users(organization=organization, sms_channel=True)
                expected_subjects = [u'DataWinners | 50 SMS Submission Limit Almost Reached: Upgrade to Continue Collecting Data via SMS!',
                    u'Your DataWinners Submission Limit is Approaching!']
                msgs = [mail.outbox.pop() for i in range(len(mail.outbox))]
                for msg in msgs:
                    self.assertIn(msg.subject, expected_subjects)