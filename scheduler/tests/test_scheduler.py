from datetime import date
from django.utils import unittest
from mock import Mock,patch
from datawinners.project.models import  Reminder, Project, RemindTo
from datawinners.scheduler.scheduler import   send_reminders_on

#TODO: reinder to be sent to only those not sent
#TODO: reinder to be sent to all ds
#TODO: exception scenarios
from datawinners.scheduler.smsclient import SMSClient

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

        self.reminder_log_patcher = patch('datawinners.scheduler.scheduler.ReminderLog')
        self.reminder_log_module = self.reminder_log_patcher.start()

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
        self.sms_client = Mock(spec=SMSClient)


    def tearDown(self):
        self.reminder_log_patcher.stop()

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

#    def test_should_send_reminders_for_all_projects_in_an_org(self):
#        all_projects = [ Mock(spec=Project),Mock(spec=Project),Mock(spec=Project) ]
#        all_reminders =  [[Reminder()],[Reminder()],[Reminder()], ]
#        reminders_per_project = { project.id: reminders  for project, reminders in zip(all_projects, all_reminders)}
#
#        Reminder.get_reminders_grouped_by_project.return_value = reminders_per_project
#
#        send_reminders_for_all_projects_for_org()
#
#        self.assertEqual(3,send_reminders_on.call_count)
#        for i,proj in enumerate(all_projects):
#            self.assertEqual(((proj,reminders_per_project[proj.id], self.mock_date,self.sms_client),{}),send_reminders_on.call_args_list[i])

