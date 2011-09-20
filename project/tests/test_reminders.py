# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
import unittest
from mock import Mock
from datawinners.project.models import Reminder, ReminderMode
from datawinners.scheduler.deadline import Deadline

class TestReminders(unittest.TestCase):
    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_deadline(self):
        today = date(2011,2,10)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE,day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011,2,12)
        self.assertTrue(reminder.should_be_send_on(deadline,today))

    def test_should_return_false_for_reminder_before_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011,2,11)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE,day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011,2,12)
        self.assertFalse(reminder.should_be_send_on(deadline,today))

    def test_should_return_true_for_reminder_after_deadline_type_if_today_is_two_days_before_deadline(self):
        today = date(2011,2,10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE,day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011,2,8)
        self.assertTrue(reminder.should_be_send_on(deadline,today))

    def test_should_return_false_for_reminder_after_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011,2,10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE,day=2)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011,2,9)
        self.assertFalse(reminder.should_be_send_on(deadline,today))

    def test_should_return_true_for_reminder_on_deadline_type_if_today_is_two_days_before_deadline(self):
        today = date(2011,2,10)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011,2,10)
        self.assertTrue(reminder.should_be_send_on(deadline,today))

    def test_should_return_false_for_reminder_on_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011,2,10)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Mock(spec=Deadline)
        deadline.current.return_value = date(2011,2,12)
        self.assertFalse(reminder.should_be_send_on(deadline,today))


