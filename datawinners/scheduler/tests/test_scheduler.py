from datetime import date

from django.utils import unittest
from mock import Mock, patch

from datawinners.accountmanagement.models import Organization, MessageTracker
from datawinners.project.models import Reminder, RemindTo, ReminderRepository, Project
from datawinners.scheduler.scheduler import send_reminders_on, send_reminders_for_an_organization


#TODO: reinder to be sent to only those not sent
#TODO: reinder to be sent to all ds
#TODO: exception scenarios
from datawinners.scheduler.smsclient import SMSClient
from mangrove.datastore.database import DatabaseManager
from datawinners.scheduler.scheduler import _get_active_paid_organization
from datawinners.sms.models import MSG_TYPE_REMINDER


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.FROM_NUMBER = "from_num"
        self.mock_date = Mock(spec=date)
        self.data_senders = [{'name': 'reporter1', 'mobile_number': 'tel1'},
                             {'name': 'reporter2', 'mobile_number': 'tel2'},
                             {'name': 'reporter3', 'mobile_number': 'tel3'},
                             {'name': 'reporter4', 'mobile_number': 'tel4'}
        ]
        self.project = Mock(spec=Project)
        self.project.get_data_senders.return_value = self.data_senders

        self.reminder1 = Mock(spec=Reminder)
        self.reminder1.should_be_send_on.return_value = True
        self.reminder1.message = 'reminder1 message'
        self.reminder1.remind_to = RemindTo.ALL_DATASENDERS
        self.reminder1.get_sender_list.return_value = self.data_senders

        self.reminder2 = Mock(spec=Reminder)
        self.reminder2.should_be_send_on.return_value = False
        self.reminder2.message = 'reminder2 message'
        self.reminder2.remind_to = RemindTo.ALL_DATASENDERS
        self.reminder2.get_sender_list.return_value = self.data_senders

        self.reminder3 = Mock(spec=Reminder)
        self.reminder3.should_be_send_on.return_value = True
        self.reminder3.message = 'reminder3 message'
        self.reminder3.remind_to = RemindTo.ALL_DATASENDERS
        self.reminder3.get_sender_list.return_value = self.data_senders

        self.reminder4 = Mock(spec=Reminder)
        self.reminder4.should_be_send_on.return_value = True
        self.reminder4.message = 'reminder4 message'
        self.reminder4.remind_to = RemindTo.ALL_DATASENDERS
        self.reminder4.get_sender_list.return_value = Exception()

        self.reminders = [self.reminder1, self.reminder2, self.reminder3]
        self.sms_client = SMSClient()
        self.sms_client.send_sms = Mock()
        self.sms_client.send_sms.return_value = True


    def tearDown(self):
        try:
            self.organization.delete()
        except Exception:
            pass

    def test_should_return_reminders_scheduled_for_the_day(self):
        reminders_sent, total_reminders_sent = send_reminders_on(self.project, self.reminders, self.mock_date,
                                                                 self.sms_client, self.FROM_NUMBER, None)

        self.assertEqual(2, len(reminders_sent))
        self.assertIn(self.reminder1, reminders_sent)
        self.assertIn(self.reminder3, reminders_sent)
        self.assertEqual(8, total_reminders_sent)

    def test_should_send_reminders_to_all_data_senders(self):
        send_reminders_on(self.project, self.reminders, self.mock_date, self.sms_client, self.FROM_NUMBER, None)

        count = 0
        for reminder in [self.reminder1, self.reminder3]:
            for ds in self.data_senders:
                self.assertEqual((("from_num", ds["mobile_number"], reminder.message, MSG_TYPE_REMINDER), {}),
                                 self.sms_client.send_sms.call_args_list[count])
                count += 1

    def test_should_send_reminders_to_only_data_senders_who_have_not_sent_in_for_period(self):
        self.reminder1.remind_to = RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS
        self.reminder3.remind_to = RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS
        who_have_not_sent_data = [self.data_senders[0], self.data_senders[3]]
        self.reminder1.get_sender_list.return_value = who_have_not_sent_data
        self.reminder3.get_sender_list.return_value = who_have_not_sent_data

        send_reminders_on(self.project, self.reminders, self.mock_date, self.sms_client, self.FROM_NUMBER, None)

        count = 0
        for reminder in [self.reminder1, self.reminder3]:
            for ds in who_have_not_sent_data:
                self.assertEqual((("from_num", ds["mobile_number"], reminder.message, MSG_TYPE_REMINDER), {}),
                                 self.sms_client.send_sms.call_args_list[count])
                count += 1

    def test_should_log_reminders_when_sent(self):
        dbm_mock = Mock(spec=DatabaseManager)
        sent_reminders, total_reminders_sent = send_reminders_on(self.project, self.reminders, self.mock_date,
                                                                 self.sms_client, self.FROM_NUMBER, dbm_mock)
        self.assertIn(self.reminder1, sent_reminders)
        self.reminder1.log.assert_called_once()

        self.assertIn(self.reminder3, sent_reminders)
        self.reminder3.log.assert_called_once()

        self.assertNotIn(self.reminder2, sent_reminders)
        self.assertEqual(0, self.reminder2.log.call_count)

    def test_get_paid_org_should_return_only_paid_org(self):

        TRIAL_ORGANIZATION_PARAMS = {'organization_name': 'myCompany',
                                     'organization_sector': 'Public Health',
                                     'organization_city': 'xian',
                                     'organization_country': 'china',
        }
        self.organization = Organization.create_trial_organization(TRIAL_ORGANIZATION_PARAMS)
        self.organization.save()
        organizations = _get_active_paid_organization()
        self.assertNotIn(self.organization, organizations)

    def test_get_active_paid_org_should_not_return_deactivate_org(self):
        ORG_DETAILS = {'organization_name': 'myCompany',
                       'organization_sector': 'Public Health',
                       'organization_city': 'xian',
                       'organization_country': 'china',
                       'organization_address': 'myAddress',
                       'organization_addressline2': 'myAddressL2',
                       'organization_state': "MyState",
                       'organization_zipcode': "1234565",
                       'organization_office_phone': "123113123",
                       'organization_website': "meme@my.com",
                       'language': "en"
        }
        deactivated_organization = Organization.create_organization(ORG_DETAILS)
        deactivated_organization.status = "Deactivated"
        deactivated_organization.save()

        activated_organization = Organization.create_organization(ORG_DETAILS)
        activated_organization.status = 'Activated'
        activated_organization.save()

        organizations = _get_active_paid_organization()

        self.assertNotIn(deactivated_organization, organizations)
        self.assertIn(activated_organization, organizations)

        activated_organization.delete()
        deactivated_organization.delete()

    def test_should_continue_with_sending_reminders_if_exception_in_prev(self):
        def expected_side_effect(*args):
            reminder_message = args[3].message
            if reminder_message == "reminder4 message":
                raise Exception()
            else:
                return 1

        self.sms_client.send_reminder = Mock()
        self.sms_client.send_reminder.side_effect = expected_side_effect

        reminders = [self.reminder1, self.reminder4, self.reminder3]
        reminders_sent, total_reminders_sent = send_reminders_on(self.project, reminders, self.mock_date,
                                                                 self.sms_client, self.FROM_NUMBER, None)
        self.assertEqual(2, len(reminders_sent))
        self.assertNotIn(self.reminder4, reminders_sent)
        self.assertIn(self.reminder1, reminders_sent)
        self.assertIn(self.reminder3, reminders_sent)

    def test_should_not_update_message_tracker_counts_if_no_reminders_are_sent_for_an_organization(self):
        org_mock = Mock(spec=Organization)
        org_mock.org_id = 'test'
        with patch("datawinners.scheduler.scheduler.get_reminder_repository") as get_reminder_repository_mock:
            reminder_repository_mock = Mock(spec=ReminderRepository)

            reminder_repository_mock.get_all_reminders_for.return_value = []

            get_reminder_repository_mock.return_value = reminder_repository_mock
            send_reminders_for_an_organization(org_mock, date.today(), self.sms_client,
                                               self.FROM_NUMBER, None)
            self.assertEqual(0, org_mock._get_message_tracker.call_count)

    def test_should_update_message_trackers_on_sending_reminders_for_organization(self):
        org_mock = Mock(spec=Organization)
        org_mock.org_id = 'test'
        dbm = Mock()
        dbm._load_document.return_value = self.project
        message_tracker_mock = Mock(spec=MessageTracker)
        org_mock._get_message_tracker.return_value = message_tracker_mock
        with patch("datawinners.scheduler.scheduler.get_reminder_repository") as get_reminder_repository_mock:
            reminder_repository_mock = Mock(spec=ReminderRepository)
            self.reminder1.project_id = 'test_project'
            reminder_repository_mock.get_all_reminders_for.return_value = [self.reminder1]
            get_reminder_repository_mock.return_value = reminder_repository_mock
            send_reminders_for_an_organization(org_mock, date.today(), self.sms_client,
                                               self.FROM_NUMBER, dbm)
            org_mock.increment_message_count_for.assert_called_once_with(sent_reminders_count=4)
