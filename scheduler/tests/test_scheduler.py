from datetime import date
from django.utils import unittest
from mock import Mock
from datawinners.project.models import  Reminder, Project
from datawinners.scheduler.scheduler import   send_reminders_on, SMSClient

#TODO: reinder to be sent to only those not sent
#TODO: reinder to be sent to all ds

class TestScheduler(unittest.TestCase):

    def setUp(self):
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

        self.reminder2 = Mock(spec=Reminder)
        self.reminder2.should_be_send_on.return_value = False
        self.reminder2.message = 'reminder2 message'

        self.reminder3 = Mock(spec=Reminder)
        self.reminder3.should_be_send_on.return_value = True
        self.reminder3.message = 'reminder3 message'

        self.reminders = [self.reminder1, self.reminder2, self.reminder3]
        self.sms_client = Mock(spec=SMSClient)


    def tearDown(self):
        pass

    def test_should_return_reminders_scheduled_for_the_day(self):
        reminders_sent = send_reminders_on(self.project,self.reminders, self.mock_date, self.sms_client)

        self.assertEqual(2,len(reminders_sent))
        self.assertIn(self.reminder1,reminders_sent)
        self.assertIn(self.reminder3,reminders_sent)

    def test_should_send_sms_for_reminders_scheduled_for_the_day(self):
        send_reminders_on(self.project, self.reminders, self.mock_date, self.sms_client)
        self.assertEqual(8,self.sms_client.send_sms.call_count)


    def test_should_send_reminders_to_all_data_senders(self):
        send_reminders_on(self.project,self.reminders, self.mock_date, self.sms_client)

        count = 0
        for reminder in [self.reminder1,self.reminder3]:
            for ds in self.data_senders:
                self.assertEqual((("from_num", ds["mobile_number"],reminder.message),{}),self.sms_client.send_sms.call_args_list[count])
                count+=1

