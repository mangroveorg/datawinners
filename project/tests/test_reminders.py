# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
import unittest
from mock import Mock
from datawinners.project.models import Reminder, ReminderMode, Project, RemindTo
from datawinners.scheduler.deadline import Deadline, Week

class TestReminders(unittest.TestCase):
    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_deadline(self):
        # same week
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(7),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_two_days_before_following_deadline(self):
        # same week
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(7),mode="Following")
        self.assertTrue(reminder.should_be_send_on(deadline, today))


    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_four_days_before_deadline(self):
        # Case where deadline is in next week, but reminder is scheduled today
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=4)
        deadline = Deadline(frequency=Week(2),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_before_deadline_type_if_today_is_on_weekend(self):
        # Case where deadline is in next week, but reminder is scheduled today
        today = date(2011, 9, 11)
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(2),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))


    def test_should_return_false_for_reminder_before_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 9, 9)
        # Sunday deadline
        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, day=1)
        deadline = Deadline(frequency=Week(7),mode="That")
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_after_deadline_type_if_today_is_two_days_after_deadline(self):
        #  same week
        today = date(2011, 9, 10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=2)
        deadline = Deadline(frequency=Week(4),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    #    2
    def test_should_return_true_for_reminder_after_deadline_type_if_today_is_three_days_after_deadline_2(self):
        # next week
        today = date(2011, 9,13 )
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=3)
        deadline = Deadline(frequency=Week(6),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))


    def test_should_return_false_for_reminder_after_deadline_type_if_today_is_not_two_days_before_deadline(self):
        today = date(2011, 9, 10)
        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, day=1)
        deadline = Deadline(frequency=Week(4),mode="That")
        self.assertFalse(reminder.should_be_send_on(deadline, today))

    def test_should_return_true_for_reminder_on_deadline_type_if_today_is_on_deadline(self):
        today = date(2011, 9, 9)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Deadline(frequency=Week(5),mode="That")
        self.assertTrue(reminder.should_be_send_on(deadline, today))

    def test_should_return_false_for_reminder_on_deadline_type_if_today_is_not_on_deadline(self):
        today = date(2011, 9, 10)
        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE)
        deadline = Deadline(frequency=Week(5),mode="That")
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

    def test_should_calculate_frequency_period_for_next_deadline_if_reminder_on_deadline(self):
        today = date(2011, 2, 10)
        project = Mock(spec=Project)
        mock_deadline = Mock(spec=Deadline)
        project.deadline.return_value = mock_deadline

        reminder = Reminder(reminder_mode=ReminderMode.ON_DEADLINE, remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS)
        reminder.get_sender_list(project, today,None)
        mock_deadline.current_deadline.assert_called_once_with(today)

    def test_should_calculate_frequency_period_for_next_deadline_if_reminder_before_deadline(self):
        today = date(2011, 2, 10)
        project = Mock(spec=Project)
        mock_deadline = Mock(spec=Deadline)
        project.deadline.return_value = mock_deadline

        reminder = Reminder(reminder_mode=ReminderMode.BEFORE_DEADLINE, remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS)
        reminder.get_sender_list(project, today,None)
        mock_deadline.next_deadline.assert_called_once_with(today)

    def test_should_calculate_frequency_period_for_current_deadline_if_reminder_after_deadline(self):
        today = date(2011, 2, 10)
        project = Mock(spec=Project)
        mock_deadline = Mock(spec=Deadline)
        project.deadline.return_value = mock_deadline

        reminder = Reminder(reminder_mode=ReminderMode.AFTER_DEADLINE, remind_to=RemindTo.DATASENDERS_WITHOUT_SUBMISSIONS)
        reminder.get_sender_list(project, today,None)
        mock_deadline.current_deadline.assert_called_once_with(today)

