from datetime import date
from datawinners.accountmanagement.models import Organization
from django.utils import unittest
from mock import Mock,patch
from datawinners.project.models import  Reminder, Project, RemindTo
from datawinners.scheduler.scheduler import   send_reminders_on

#TODO: reinder to be sent to only those not sent
#TODO: reinder to be sent to all ds
#TODO: exception scenarios
from datawinners.scheduler.smsclient import SMSClient
from mangrove.datastore.database import DatabaseManager
from datawinners.scheduler.scheduler import _get_paid_organization

class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.FROM_NUMBER = "from_num"
        self.mock_date = Mock(spec=date)
        self.data_senders = [  {  'name' : 'reporter1', 'mobile_number' : 'tel1' },
         {  'name' : 'reporter2', 'mobile_number' : 'tel2' },
         {  'name' : 'reporter3', 'mobile_number' : 'tel3' },
             {  'name' : 'reporter4', 'mobile_number' : 'tel4' }
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

        self.reminders = [self.reminder1, self.reminder2, self.reminder3]
        self.sms_client = SMSClient()
        self.sms_client.send_sms=Mock()
        self.sms_client.send_sms.return_value=True


    def tearDown(self):
        try:
            self.organization.delete()
        except :
            pass

    def test_should_return_reminders_scheduled_for_the_day(self):
        reminders_sent = send_reminders_on(self.project,self.reminders, self.mock_date, self.sms_client,self.FROM_NUMBER,None)

        self.assertEqual(2,len(reminders_sent))
        self.assertIn(self.reminder1,reminders_sent)
        self.assertIn(self.reminder3,reminders_sent)

    def test_should_send_sms_for_reminders_scheduled_for_the_day(self):
        send_reminders_on(self.project, self.reminders, self.mock_date, self.sms_client,self.FROM_NUMBER,None)
        self.assertEqual(8,self.sms_client.send_sms.call_count)


    def test_should_send_reminders_to_all_data_senders(self):
        send_reminders_on(self.project,self.reminders, self.mock_date, self.sms_client,self.FROM_NUMBER,None)

        count = 0
        for reminder in [self.reminder1,self.reminder3]:
            for ds in self.data_senders:
                self.assertEqual((("from_num", ds["mobile_number"],reminder.message),{}),self.sms_client.send_sms.call_args_list[count])
                count+=1

    def test_should_send_reminders_to_only_data_senders_who_have_not_sent_in_for_period(self):
        self.reminder1.remind_to = RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS
        self.reminder3.remind_to = RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS
        who_have_not_sent_data = [self.data_senders[0],self.data_senders[3]]
        self.reminder1.get_sender_list.return_value = who_have_not_sent_data
        self.reminder3.get_sender_list.return_value = who_have_not_sent_data

        send_reminders_on(self.project,self.reminders, self.mock_date, self.sms_client,self.FROM_NUMBER,None)

        count = 0
        for reminder in [self.reminder1,self.reminder3]:
            for ds in who_have_not_sent_data:
                self.assertEqual((("from_num", ds["mobile_number"],reminder.message),{}),self.sms_client.send_sms.call_args_list[count])
                count+=1

    def test_should_log_reminders_when_sent(self):
        dbm_mock = Mock(spec=DatabaseManager)
        send_reminders_on(self.project,self.reminders, self.mock_date, self.sms_client,self.FROM_NUMBER, dbm_mock)
        self.reminder1.log.assert_called_once()
        self.reminder3.log.assert_called_once()
        self.assertEqual(0,self.reminder2.log.call_count)

    def test_get_paid_org_should_return_only_paid_org(self):

        TRIAL_ORGANIZATION_PARAMS = {'organization_name': 'myCompany',
                                 'organization_sector': 'Public Health',
                                 'organization_city': 'xian',
                                 'organization_country': 'china',
                                 }
        self.organization = Organization.create_trial_organization(TRIAL_ORGANIZATION_PARAMS)
        self.organization.save()
        organizations = _get_paid_organization()
        self.assertNotIn(self.organization,organizations)