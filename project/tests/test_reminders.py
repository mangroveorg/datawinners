# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
import unittest
from mock import Mock
from datawinners.project.models import Reminder, ReminderMode, Project, RemindTo
from datawinners.scheduler.deadline import Deadline

class TestReminders(unittest.TestCase):
    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_deadline(self):
        today = date(2011, 9, 9)
        # Sunday deadline
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 9, 11)
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_deadline_1(self):
        today = date(2011, 9, 11)
        # Tuesday deadline, so reminder will be in previous week, deadline is 2011.9.13
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 9, 6)
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_false_for_reminder_before_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 9, 10)
        # Sunday deadline
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 9, 11)
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_after_deadline_type_if_today_is_two_days_after_deadline(self):
        today = date(2011, 2, 10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 2, 8)
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_false_for_reminder_after_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 2, 10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 2, 9)
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_on_deadline_type_if_today_is_two_days_before_deadline(self):
        today = date(2011, 2, 10)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 2, 10)
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_false_for_reminder_on_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 2, 10)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011, 2, 12)
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_all_data_senders_as_sender_list_if_remind_to_mode_is_all_datasenders(self):
        data_senders = [{'name': 'reporter1', 'mobile_number': 'tel1'},
                {'name': 'reporter2', 'mobile_number': 'tel2'},
                {'name': 'reporter3', 'mobile_number': 'tel3'},
                {'name': 'reporter4', 'mobile_number': 'tel4'}
        ]
        today = date(2011, 2, 10)
        project = Mock(spec=Project)
        project.get_data_senders.return_value = data_senders
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        self.assertEqual(data_senders, reminder.get_sender_list(project, today,None))

    def test_should_return_data_senders_as_sender_list_if_remind_to_mode_is_datasenders_without_submissions(self):
        data_senders = [{'name': 'reporter1', 'mobile_number': 'tel1'},
                {'name': 'reporter2', 'mobile_number': 'tel2'},
                {'name': 'reporter3', 'mobile_number': 'tel3'},
                {'name': 'reporter4', 'mobile_number': 'tel4'}
        ]
        today = date(2011, 2, 10)
        project = Mock(spec=Project)
        expected_sender_list = [data_senders[0], data_senders[2]]
        project.get_data_senders_without_submissions_for.return_value = expected_sender_list
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE, remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS)
        self.assertEqual(expected_sender_list, reminder.get_sender_list(project, today,None))

